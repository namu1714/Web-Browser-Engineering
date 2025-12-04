import tkinter

from globals import HEIGHT, SCROLL_STEP, VSTEP, WIDTH
from layout import Layout
from parser import HTMLParser, print_tree


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
    nodes = HTMLParser(body).parse()
    print_tree(nodes)  # For debugging: print the parse tree
    self.display_list = Layout(nodes).display_list
    self.compute_max_scroll() 
    self.draw()

  def compute_max_scroll(self):
    max_y = max(y for _, y, _, _ in self.display_list)
    self.max_scroll = max_y - self.height + VSTEP

  def draw(self):
    self.canvas.delete("all")
    for x, y, word, font in self.display_list:
      if y - self.scroll > self.height:
        continue
      if y + VSTEP < self.scroll:
        continue
      self.canvas.create_text(x, y - self.scroll, text=word, font=font, anchor="nw")
  
  def scrolldown(self, e):
    self.scroll += SCROLL_STEP
    if self.scroll > self.max_scroll:
      self.scroll = self.max_scroll
    self.draw()

  def scrollup(self, e):
    self.scroll -= SCROLL_STEP
    if self.scroll < 0:
      self.scroll = 0
    self.draw()


