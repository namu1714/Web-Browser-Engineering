import tkinter.font

from globals import HSTEP, VSTEP, WIDTH
from parser import Text

FONTS = {}

class Layout:
  def __init__(self, tokens):
    self.tokens = tokens
    self.display_list = []
    self.line = []
    self.cursor_x = HSTEP
    self.cursor_y = VSTEP
    self.weight = "normal"
    self.style = "roman"
    self.size = 12

    for tok in self.tokens:
      self.token(tok)

  def token(self, tok):
    if isinstance(tok, Text):
      for word in tok.text.split():
        self.word(word)
    elif tok.tag == "i":
      self.style = "italic"
    elif tok.tag == "/i":
      self.style = "roman"
    elif tok.tag == "b":
      self.weight = "bold"
    elif tok.tag == "/b":
      self.weight = "normal"
    elif tok.tag == "small":
      self.size -= 2
    elif tok.tag == "/small":
      self.size += 2
    elif tok.tag == "big":
      self.size += 4
    elif tok.tag == "/big":
      self.size -= 4
    elif tok.tag == "br":
      self.flush()
    elif tok.tag == "/p":
      self.flush()
      self.cursor_y += VSTEP

  def word(self, word):
    font = get_font(self.size, self.weight, self.style)
    w = font.measure(word)
    if self.cursor_x + w > WIDTH - HSTEP:
      self.flush()
    self.line.append((self.cursor_x, word, font))
    self.cursor_x += w + font.measure(" ")

  def flush(self):
    if not self.line: 
      return
    metrics = [font.metrics() for x, word, font in self.line]
    # Calculate the baseline for the line based on the maximum ascent
    max_ascent = max([metric["ascent"] for metric in metrics])
    baseline = self.cursor_y + 1.25 * max_ascent
    for x, word, font in self.line:
      y = baseline - font.metrics("ascent")
      self.display_list.append((x, y, word, font))
    max_descent = max([metric["descent"] for metric in metrics])
    self.cursor_y = baseline + 1.25 * max_descent
    self.cursor_x = HSTEP
    self.line = []

def get_font(size, weight, style):
  key = (size, weight, style)
  if key not in FONTS:
    font = tkinter.font.Font(size=size, weight=weight, slant=style)
    label = tkinter.Label(font=font)
    FONTS[key] = (font, label)
  return FONTS[key][0]
