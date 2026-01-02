import tkinter

from globals import HEIGHT, SCROLL_STEP, VSTEP, WIDTH
from layout import DocumentLayout
from parser import HTMLParser

class Browser:
  def __init__(self):
    self.window = tkinter.Tk()

    self.width, self.height = WIDTH, HEIGHT
    self.canvas = tkinter.Canvas(self.window, width=self.width, height=self.height)
    self.canvas.pack(fill="both", expand=True)

    self.scroll = 0
    self.max_scroll = 0
    self.window.bind("<Down>", self.scrolldown)
    self.window.bind("<Up>", self.scrollup)
    
  def load(self, url):
    body = url.request()
    self.nodes = HTMLParser(body).parse()

    self.document = DocumentLayout(self.nodes)
    self.document.layout()
    self.display_list = []
    paint_tree(self.document, self.display_list)

    self.draw()

  def draw(self):
    self.canvas.delete("all")
    for cmd in self.display_list:
      if cmd.top > self.scroll + HEIGHT:
        continue
      if cmd.bottom < self.scroll:
        continue
      cmd.execute(self.scroll, self.canvas)
  
  def scrolldown(self, e):
    max_y = max(self.document.height + 2*VSTEP - HEIGHT, 0)
    self.scroll = min(self.scroll + SCROLL_STEP, max_y)
    self.draw()

  def scrollup(self, e):
    self.scroll -= SCROLL_STEP
    if self.scroll < 0:
      self.scroll = 0
    self.draw()

def paint_tree(layout_object, display_list):
  display_list.extend(layout_object.paint())

  for child in layout_object.children:
    paint_tree(child, display_list)
