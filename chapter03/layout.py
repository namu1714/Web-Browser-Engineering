import tkinter.font

from globals import HSTEP, VSTEP, WIDTH

# Example 3-1: Support for centered text alignment & <h1> tag
# Example 3-2: Support for <sup> tag (superscript)

FONTS = {}

class Text:
  def __init__(self, text):
    self.text = text

class Tag:
  def __init__(self, tag):
    self.tag = tag

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
    self.is_sup = False  # Track if inside <sup> tag

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
    elif tok.tag == "sup":
      self.is_sup = True
      self.size -= 4
    elif tok.tag == "/sup":
      self.is_sup = False
      self.size += 4
    elif tok.tag.startswith("h1"):
      self.flush()  # Ensure <h1> starts on a new line
      self.size += 4  # Increase font size for <h1>
      self.weight = "bold"
    elif tok.tag == "/h1":
      self.flush()  # Ensure content after <h1> starts on a new line
      self.size -= 4  # Reset font size after <h1>
      self.weight = "normal"

  def word(self, word):
    font = get_font(self.size, self.weight, self.style)
    w = font.measure(word)
    if self.cursor_x + w > WIDTH - HSTEP:
      self.flush()
    self.line.append((self.cursor_x, word, font, self.is_sup))
    self.cursor_x += w + font.measure(" ")

  def flush(self):
    if not self.line:
      return
    
    self.center_text()

    metrics = [font.metrics() for x, word, font, is_sup in self.line]
    max_ascent = max([metric["ascent"] for metric in metrics])
    baseline = self.cursor_y + 1.25 * max_ascent

    for x, word, font, is_sup in self.line:
      y = baseline - font.metrics("ascent")
      if is_sup:  # Adjust y position for <sup> tag
        y -= VSTEP // 2
      self.display_list.append((x, y, word, font))

    max_descent = max([metric["descent"] for metric in metrics])
    self.cursor_y = baseline + 1.25 * max_descent
    self.cursor_x = HSTEP
    self.line = []

  def center_text(self):
    if not self.line:
      return

    # Calculate total width of the line
    total_width = sum(font.measure(word) + font.measure(" ") for x, word, font, is_sup in self.line)
    total_width -= self.line[-1][2].measure(" ")  # Remove trailing space width

    # Calculate starting x position for centered alignment
    start_x = (WIDTH - total_width) // 2

    # Adjust x positions of words in the line
    adjusted_line = []
    for x, word, font, is_sup in self.line:
      adjusted_line.append((start_x, word, font, is_sup))
      start_x += font.measure(word) + font.measure(" ")

    self.line = adjusted_line

def lex(body):
  out = []
  buffer = ""
  in_tag = False
  for c in body:
    if c == "<":
      in_tag = True
      if buffer: out.append(Text(buffer))
      buffer = ""
    elif c == ">":
      in_tag = False
      out.append(Tag(buffer))
      buffer = ""
    else:
      buffer += c
  if not in_tag and buffer:
    out.append(Text(buffer))
  return out

def get_font(size, weigit, style):
  key = (size, weigit, style)
  if key not in FONTS:
    font = tkinter.font.Font(size=size, weight=weigit, slant=style)
    label = tkinter.Label(font=font)
    FONTS[key] = (font, label)
  return FONTS[key][0]
