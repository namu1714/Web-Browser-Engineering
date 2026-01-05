import tkinter.font

from globals import HSTEP, VSTEP, WIDTH
from parser import Text, Element

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
    self.display_list = []

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
    # 1. Set position and width of this block
    self.x = self.parent.x
    self.width = self.parent.width

    if self.previous:
      self.y = self.previous.y + self.previous.height
    else:
      self.y = self.parent.y

    mode = self.layout_mode()

    # 2. Layout according to mode
    if mode == "block":
      previous = None
      for child in self.node.children:
        next = BlockLayout(child, self, previous)
        self.children.append(next)
        previous = next
    else: 
      self.cursor_x = 0
      self.cursor_y = 0
      self.weight = "normal"
      self.style = "roman"
      self.size = 12

      # Add spacing after bullet for list items
      if isinstance(self.node, Element) and self.node.tag == "li":
        self.cursor_x = 16

      self.line = []
      self.recurse(self.node)
      self.flush()

    # 3. Layout children
    for child in self.children:
      child.layout()

    # 4. Compute height - it depends on children' layout
    if mode == "block":
      self.height = sum([
        child.height for child in self.children
      ])
    else:
      self.height = self.cursor_y

  def layout_intermediate(self):
    previous = None
    for child in self.node.children:
      next = BlockLayout(child, self, previous)
      self.children.append(next)
      previous = next

  def recurse(self, tree):
    if isinstance(tree, Text):
      for word in tree.text.split():
        self.word(word)
    else:
      self.open_tag(tree.tag)
      for child in tree.children:
        self.recurse(child)
      self.close_tag(tree.tag)

  def open_tag(self, tag):
    if tag == "i":
      self.style = "italic"
    elif tag == "b":
      self.weight = "bold"
    elif tag == "small":
      self.size -= 2
    elif tag == "big":
      self.size += 4
    elif tag == "br":
      self.flush()
  
  def close_tag(self, tag):
    if tag == "i":
      self.style = "roman"
    elif tag == "b":
      self.weight = "normal"
    elif tag == "small":
      self.size += 2
    elif tag == "big":
      self.size -= 4
    elif tag == "p":
      self.flush()
      self.cursor_y += VSTEP

  def word(self, word):
    font = get_font(self.size, self.weight, self.style)
    w = font.measure(word)
    if self.cursor_x + w > self.width:
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
    for rel_x, word, font in self.line:
      x = self.x + rel_x
      y = self.y + baseline - font.metrics("ascent")
      self.display_list.append((x, y, word, font))
    max_descent = max([metric["descent"] for metric in metrics])
    self.cursor_y = baseline + 1.25 * max_descent
    self.cursor_x = 0
    self.line = []

  def paint(self):
    cmds = []
    if isinstance(self.node, Element) and self.node.tag == "pre":
      x2, y2 = self.x + self.width, self.y + self.height
      rect = DrawRect(self.x, self.y, x2, y2, "lightgray")
      cmds.append(rect)
    if isinstance(self.node, Element) and self.node.tag == "nav" and \
       self.node.attributes.get("class") == "links":
      x2, y2 = self.x + self.width, self.y + self.height
      rect = DrawRect(self.x, self.y, x2, y2, "lightgray")
      cmds.append(rect)
    if isinstance(self.node, Element) and self.node.tag == "li":
      # Draw bullet point (small square)
      bullet_x = self.x 
      bullet_y = self.y
      font = get_font(12, "normal", "roman")
      bullet = DrawText(bullet_x, bullet_y, "▪", font)
      cmds.append(bullet)
    if self.layout_mode() == "inline":
      for x, y, word, font in self.display_list:
        cmds.append(DrawText(x, y, word, font))
    return cmds
  

class DrawText:
  def __init__(self, x1, y1, text, font):
    self.top = y1
    self.left = x1
    self.text = text
    self.font = font

    self.bottom = y1 + font.metrics("linespace")

  def execute(self, scroll, canvas):
    canvas.create_text(self.left, self.top - scroll,
                       text=self.text, font=self.font, anchor="nw")


class DrawRect:
  def __init__(self, x1, y1, x2, y2, color):
    self.top = y1
    self.left = x1
    self.bottom = y2
    self.right = x2
    self.color = color

  def execute(self, scroll, canvas):
    canvas.create_rectangle(self.left, self.top - scroll,
                            self.right, self.bottom - scroll,
                            width=0, fill=self.color)


def get_font(size, weight, style):
  key = (size, weight, style)
  if key not in FONTS:
    font = tkinter.font.Font(size=size, weight=weight, slant=style)
    label = tkinter.Label(font=font)
    FONTS[key] = (font, label)
  return FONTS[key][0]
