import tkinter

from globals import HEIGHT, SCROLL_STEP, VSTEP, WIDTH, tree_to_list
from layout import DocumentLayout
from parser import HTMLParser, Element, Text
from css import CSSParser, cascade_priority, style

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()

class Browser:
  def __init__(self):
    self.window = tkinter.Tk()

    self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT, bg="white")
    self.canvas.pack(fill="both", expand=True)

    self.window.bind("<Down>", self.handle_down)
    # self.window.bind("<Up>", self.handle_up) # implement later
    self.window.bind("<Button-1>", self.handle_click)

    self.tabs = []
    self.active_tab = None

  def handle_down(self, e):
    self.active_tab.scrolldown()
    self.draw()

  def handle_click(self, e):
    self.active_tab.click(e.x, e.y)
    self.draw()

  def draw(self):
    self.active_tab.draw(self.canvas)

  def new_tab(self, url):
    new_tab = Tab()
    new_tab.load(url)
    self.active_tab = new_tab
    self.tabs.append(new_tab)
    self.draw()


class Tab:
  def __init__(self):

    self.scroll = 0
    self.max_scroll = 0

    self.url = None
    
  def load(self, url):
    self.url = url
    body = url.request()
    self.nodes = HTMLParser(body).parse()

    rules = DEFAULT_STYLE_SHEET.copy()
    links = [node.attributes["href"]
             for node in tree_to_list(self.nodes, [])
             if isinstance(node, Element)
             and node.tag == "link"
             and node.attributes.get("rel") == "stylesheet"
             and "href" in node.attributes]
    for link in links:
      style_url = url.resolve(link)
      try:
        body = style_url.request()
      except:
        continue
      rules.extend(CSSParser(body).parse())

    style(self.nodes, sorted(rules, key=cascade_priority))
    self.document = DocumentLayout(self.nodes)
    self.document.layout()
    self.display_list = []
    paint_tree(self.document, self.display_list)
  

  def draw(self, canvas):
    for cmd in self.display_list:
      if cmd.top > self.scroll + HEIGHT:
        continue
      if cmd.bottom < self.scroll:
        continue
      cmd.execute(self.scroll, canvas)
  
  def scrolldown(self):
    max_y = max(self.document.height + 2*VSTEP - HEIGHT, 0)
    self.scroll = min(self.scroll + SCROLL_STEP, max_y)

  def scrollup(self, e):
    self.scroll -= SCROLL_STEP
    if self.scroll < 0:
      self.scroll = 0
  
  def click(self, x, y):
    y += self.scroll
    objs = [obj for obj in tree_to_list(self.document, [])
            if obj.x <= x < obj.x + obj.width
            and obj.y <= y < obj.y + obj.height]
    if not objs:
      return
    elt = objs[-1].node
    while elt:
      if isinstance(elt, Text):
        pass
      elif elt.tag == "a" and "href" in elt.attributes:
        url = self.url.resolve(elt.attributes["href"])
        return self.load(url)
      elt = elt.parent


def paint_tree(layout_object, display_list):
  display_list.extend(layout_object.paint())

  for child in layout_object.children:
    paint_tree(child, display_list)
