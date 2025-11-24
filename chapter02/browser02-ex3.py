import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__))) # Adjust the import path

from url import URL
import tkinter

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
NEWLINE_STEP = 20
SCROLL_STEP = 100

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

    self.window.bind("<Configure>", self.on_resize)
    
  def load(self, url):
    body = url.request()
    self.text = self.lex(body)
    self.display_list = layout(self.text, self.width)
    self.compute_max_scroll()
    self.draw()

  def on_resize(self, event):
    # Configure 이벤트가 여러 위젯에서 오므로, 윈도우에서 온 것만 처리
    if event.widget is self.window:
      self.width = event.width
      self.height = event.height
      self.display_list = layout(self.text, self.width)
      self.compute_max_scroll()
      self.draw()

  def compute_max_scroll(self):
    max_y = max(y for _, y, _ in self.display_list)
    self.max_scroll = max_y - self.height + VSTEP

  def draw(self):
    self.canvas.delete("all")
    for x, y, c in self.display_list:
      if y - self.scroll > self.height:
        continue
      if y + VSTEP < self.scroll:
        continue
      self.canvas.create_text(x, y - self.scroll, text=c)
  
  def lex(self, body):
    text = ""
    in_tag = False
    for c in body:
      if c == "<":
        in_tag = True
      elif c == ">":
        in_tag = False
      elif not in_tag:
        text += c
    return text
  
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


def layout(text, width):
  display_list = []
  curser_x, curser_y = HSTEP, VSTEP
  for c in text:
    if c == "\n":
      curser_y += NEWLINE_STEP
      curser_x = HSTEP
      continue
    display_list.append((curser_x, curser_y, c))
    curser_x += HSTEP
    if curser_x > width - HSTEP:
      curser_y += VSTEP
      curser_x = HSTEP
  return display_list


if __name__ == "__main__":
  import sys
  Browser().load(URL(sys.argv[1]))
  tkinter.mainloop()
