import tkinter
from parser import Element, HTMLParser, Text

from css import CSSParser, cascade_priority, style
from globals import HEIGHT, SCROLL_STEP, VSTEP, WIDTH, Rect, tree_to_list
from layout import (DocumentLayout, DrawLine, DrawOutline, DrawRect, DrawText,
                    get_font)
from url import URL

DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()

 # A simple Chrome wrapper for the browser
class Chrome:
  def __init__(self, browser):
    self.browser = browser
    self.font = get_font(20, "normal", "roman")
    self.font_height = self.font.metrics("linespace")
    self.padding = 5
    self.tabbar_top = 0
    self.tabbar_bottom = self.font_height + 2 * self.padding

    plus_width = self.font.measure("+") + 2 * self.padding
    self.newtab_rect = Rect(
      left = self.padding, 
      top = self.padding,
      width = plus_width,
      height = self.font_height
    )
    self.bottom = self.tabbar_bottom
  
  def tab_rect(self, i):
    tabs_start = self.newtab_rect.right + self.padding
    tab_width = self.font.measure("Tab X") + 2 * self.padding
    return Rect(
      left = tabs_start + tab_width * i,
      top = self.tabbar_top,
      width = tabs_start + tab_width * (i + 1),
      height = self.tabbar_bottom - self.tabbar_top
    )
  
  def paint(self):
    cmds = []
    cmds.append(DrawRect(
      Rect(0, 0, WIDTH, self.bottom), 
      "white"))
    cmds.append(DrawLine(
      0, self.bottom, WIDTH, self.bottom,
      "black", 1))

    cmds.append(DrawOutline(self.newtab_rect, "black", 1))
    cmds.append(DrawText(
        self.newtab_rect.left + self.padding,
        self.newtab_rect.top,
        "+", self.font, "black"))
    
    for i, tab in enumerate(self.browser.tabs):
      bounds = self.tab_rect(i)
      cmds.append(DrawLine(
        bounds.left, 0, bounds.left, bounds.bottom,
        "black", 1))
      cmds.append(DrawLine(
        bounds.right, 0, bounds.right, bounds.bottom,
        "black", 1))
      cmds.append(DrawText(
        bounds.left + self.padding, bounds.top + self.padding,
        "Tab {}".format(i), self.font, "black"
      ))
      if tab == self.browser.active_tab:
        cmds.append(DrawLine(
          0, bounds.bottom, bounds.left, bounds.bottom,
          "black", 1))
        cmds.append(DrawLine(
          bounds.right, bounds.bottom, WIDTH, bounds.bottom,
          "black", 1))
    return cmds

  def click(self, x, y):
    if self.newtab_rect.containsPoint(x, y):
      self.browser.new_tab(URL("https://browser.engineering/"))
    else:
      for i, tab in enumerate(self.browser.tabs):
        if self.tab_rect(i).containsPoint(x, y):
          self.browser.active_tab = tab
          break
    

# A simple browser with tabs
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
    self.chrome = Chrome(self)

  def handle_down(self, e):
    self.active_tab.scrolldown()
    self.draw()

  def handle_click(self, e):
    if e.y < self.chrome.bottom:
      self.chrome_click(e.x, e.y)
    else:
      tab_y = e.y - self.chrome.bottom
      self.active_tab.click(e.x, tab_y)
    self.draw()

  def draw(self):
    self.canvas.delete("all")
    self.active_tab.draw(self.canvas, self.chrome.bottom)
    for cmd in self.chrome.paint():
      cmd.execute(0, self.canvas)

  def new_tab(self, url):
    new_tab = Tab(HEIGHT - self.chrome.bottom)
    new_tab.load(url)
    self.active_tab = new_tab
    self.tabs.append(new_tab)
    self.draw()


class Tab:
  def __init__(self, tab_height):

    self.scroll = 0
    self.max_scroll = 0

    self.url = None
    self.tab_height = tab_height
    
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
  

  def draw(self, canvas, offset):
    for cmd in self.display_list:
      if cmd.top > self.scroll + self.tab_height:
        continue
      if cmd.bottom < self.scroll:
        continue
      cmd.execute(self.scroll - offset, canvas)
  
  def scrolldown(self):
    max_y = max(self.document.height + 2*VSTEP - self.tab_height, 0)
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
    paint_tree(child, display_list)
