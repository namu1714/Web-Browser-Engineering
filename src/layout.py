import tkinter.font
from parser import Element, Text

from globals import HSTEP, VSTEP, WIDTH, Rect

FONTS = {}
BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

class DocumentLayout:
  def __init__(self, node):
    self.node = node
    self.parent = None
    self.children = []
  
  def layout(self):
    child = BlockLayout(self.node, self, None)
    self.children.append(child)

    self.width = WIDTH - 2*HSTEP
    self.x = HSTEP
    self.y = VSTEP
    child.layout()
    self.height = child.height

  def paint(self):
    return []


class BlockLayout:
  def __init__(self, node, parent, previous):
    self.node = node
    self.parent = parent
    self.previous = previous
    self.children = []

    self.x = None
    self.y = None
    self.width = None
    self.height = None

  def layout_mode(self):
    if isinstance(self.node, Text):
      return "inline"
    elif any ([isinstance(child, Element) and \
               child.tag in BLOCK_ELEMENTS for child in self.node.children]):
      return "block"
    elif self.node.children: # has children but none are block
      return "inline"
    else:
      return "block" # empty element

  def layout(self):
    self.x = self.parent.x
    self.width = self.parent.width

    if self.previous:
      self.y = self.previous.y + self.previous.height
    else:
      self.y = self.parent.y

    mode = self.layout_mode()

    if mode == "block":
      previous = None
      for child in self.node.children:
        next = BlockLayout(child, self, previous)
        self.children.append(next)
        previous = next
    else: 
      self.cursor_x = 0
      self.weight = "normal"
      self.style = "roman"
      self.size = 12

      self.new_line()
      self.recurse(self.node)

    for child in self.children:
      child.layout()

    self.height = sum([child.height for child in self.children])

  def layout_intermediate(self):
    previous = None
    for child in self.node.children:
      next = BlockLayout(child, self, previous)
      self.children.append(next)
      previous = next

  def recurse(self, node):
    if isinstance(node, Text):
      for word in node.text.split():
        self.word(node, word)
    else:
      for child in node.children:
        self.recurse(child)

  def word(self, node, word):
    weight = node.style["font-weight"]
    style = node.style["font-style"]
    if style == "normal": style = "roman"
    size = int(float(node.style["font-size"][:-2]) * .75)
    font = get_font(size, weight, style)

    w = font.measure(word)
    if self.cursor_x + w > self.width:
      self.new_line()

    line = self.children[-1]
    previous_word = line.children[-1] if line.children else None
    text = TextLayout(node, word, line, previous_word)
    line.children.append(text)
    self.cursor_x += w + font.measure(" ")

  def new_line(self):
    self.cursor_x = 0
    last_line = self.children[-1] if self.children else None
    new_line = LineLayout(self.node, self, last_line)
    self.children.append(new_line)

  def self_rect(self):
    return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

  def paint(self):
    cmds = []
    bgcolor = self.node.style.get("background-color", "transparent")

    if bgcolor != "transparent":
      rect = DrawRect(self.self_rect(), bgcolor)
      cmds.append(rect)

    return cmds
  
class LineLayout:
  def __init__(self, node, parent, previous):
    self.node = node
    self.parent = parent
    self.previous = previous
    self.children = []

  def layout(self):
    self.width = self.parent.width
    self.x = self.parent.x

    if self.previous:
      self.y = self.previous.y + self.previous.height
    else:
      self.y = self.parent.y
    
    for word in self.children:
      word.layout()

    # Calculate the baseline for the line based on the maximum ascent
    max_ascent = max([word.font.metrics("ascent") for word in self.children])
    baseline = self.y + 1.25 * max_ascent
    for word in self.children:
      word.y = baseline - word.font.metrics("ascent")
    max_descent = max([word.font.metrics("descent") for word in self.children])
    self.height = 1.25 * (max_ascent + max_descent)

  def paint(self):
    return []


class TextLayout:
  def __init__(self, node, word, parent, previous):
    self.node = node
    self.word = word
    self.parent = parent
    self.previous = previous
    self.children = []
    self.font = None
  
  def layout(self):
    weight = self.node.style["font-weight"]
    style = self.node.style["font-style"]
    if style == "normal": style = "roman"
    size = int(float(self.node.style["font-size"][:-2]) * .75)
    self.font = get_font(size, weight, style)
    self.width = self.font.measure(self.word)

    if self.previous:
      space = self.previous.font.measure(" ")
      self.x = self.previous.x + space + self.previous.width
    else:
      self.x = self.parent.x
    
    self.height = self.font.metrics("linespace")

  def paint(self):
    color = self.node.style["color"]
    return [DrawText(self.x, self.y, self.word, self.font, color)]
  

class DrawText:
  def __init__(self, x1, y1, text, font, color):
    self.top = y1
    self.left = x1
    self.text = text
    self.font = font
    self.color = color

    self.bottom = y1 + font.metrics("linespace")

  def execute(self, scroll, canvas):
    canvas.create_text(self.left, self.top - scroll,
                       text=self.text, font=self.font, fill=self.color, 
                       anchor="nw")


class DrawRect:
  def __init__(self, rect, color):
    self.rect = rect
    self.color = color

  def execute(self, scroll, canvas):
    canvas.create_rectangle(self.rect.left, self.rect.top - scroll,
                            self.rect.right, self.rect.bottom - scroll,
                            width=0, fill=self.color)
    
    
class DrawOutline:
  def __init__(self, rect, color, thickness):
    self.rect = rect
    self.color = color
    self.thickness = thickness

  def execute(self, scroll, canvas):
    canvas.create_rectangle(
      self.rect.left, 
      self.rect.top - scroll,
      self.rect.right,
      self.rect.bottom - scroll,
      width=self.thickness, outline=self.color
    )


class DrawLine:
  def __init__(self, x1, y1, x2, y2, color, thickness):
    self.rect = Rect(x1, y1, x2, y2)
    self.color = color
    self.thickness = thickness

  def execute(self, scroll, canvas):
    canvas.create_line(
      self.rect.left, 
      self.rect.top - scroll,
      self.rect.right,
      self.rect.bottom - scroll,
      width=self.thickness, fill=self.color
    )


def get_font(size, weight, style):
  key = (size, weight, style)
  if key not in FONTS:
    font = tkinter.font.Font(size=size, weight=weight, slant=style)
    label = tkinter.Label(font=font)
    FONTS[key] = (font, label)
  return FONTS[key][0]
