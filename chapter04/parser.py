class Text:
  def __init__(self, text, parent):
    self.text = text
    self.children = []
    self.parent = parent # not used in text, but kept for consistency with Element

  def __repr__(self):
    return repr(self.text)


class Element:
  def __init__(self, tag, attributes, parent):
    self.tag = tag
    self.attributes = attributes
    self.children = []
    self.parent = parent

  def __repr__(self):
    return "<" + self.tag + ">"


def print_tree(node, indent=0):
  print(" " * indent + repr(node))
  for child in node.children:
    print_tree(child, indent + 2)


class HTMLParser:
  SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
  ]
  HEAD_TAGS = [
      "base", "basefont", "bgsound", "noscript",
      "link", "meta", "title", "style", "script",
  ]

  def __init__(self, body):
    self.body = body
    self.unfinished = []

  def parse(self):
    text = "" 
    in_tag = False
    i = 0

    while i < len(self.body):
      c = self.body[i]
      
      # Check for comment start
      if c == "<" and i + 3 < len(self.body) and self.body[i:i+4] == "<!--":
        if text and not in_tag:
          self.add_text(text)
          text = ""
        # Find comment end
        end = self.body.find("-->", i + 4)
        if end != -1:
          i = end + 3
          continue
        else:
          # Malformed comment, skip to end
          break
      elif c == "<":
        in_tag = True
        if text: self.add_text(text)
        text = ""
      elif c == ">":
        in_tag = False
        self.add_tag(text)
        text = ""
      else:
        text += c
      i += 1
      
    if not in_tag and text:
        self.add_text(text)
    return self.finish()
  
  def add_text(self, text):
    if text.isspace():
      return
    self.implicit_tags(None)
    parent = self.unfinished[-1]
    node = Text(text, parent)
    parent.children.append(node)

  def add_tag(self, tag):
    tag, attributes = self.get_attributes(tag)
    if tag.startswith("!"): # comment or doctype
      return
    self.implicit_tags(tag)
    if tag.startswith("/"): # closing tag
      if len(self.unfinished) == 1: 
        return
      node = self.unfinished.pop()
      parent = self.unfinished[-1]
      parent.children.append(node)
    elif tag in self.SELF_CLOSING_TAGS: 
      parent = self.unfinished[-1]
      node = Element(tag, attributes, parent)
      parent.children.append(node)
    else: # opening tag
      parent = self.unfinished[-1] if self.unfinished else None
      node = Element(tag, attributes, parent)
      self.unfinished.append(node)
  
  def get_attributes(self, text):
    parts = text.split()
    tag = parts[0].casefold()
    attributes = {}
    for attrpair in parts[1:]:
      if "=" in attrpair:
        key, value = attrpair.split("=", 1)
        if len(value) > 2 and value[0] in ["'", "\""]:
          value = value[1:-1]
        attributes[key.casefold()] = value
      else:
        attributes[attrpair.casefold()] = ""
    return tag, attributes

  def implicit_tags(self, tag):
    while True:
      open_tags = [node.tag for node in self.unfinished]
      if open_tags == [] and tag != "html":
        self.add_tag("html")
      elif open_tags == ["html"] \
        and tag not in ["head", "body", "/html"]:
        if tag in self.HEAD_TAGS:
          self.add_tag("head")
        else:
          self.add_tag("body")
      elif open_tags == ["html", "head"] and \
          tag not in ["/head"] + self.HEAD_TAGS:
        self.add_tag("/head")
      else:
        break
  
  def finish(self):
    if not self.unfinished:
      self.implicit_tags(None)
    while len(self.unfinished) > 1:
      node = self.unfinished.pop()
      parent = self.unfinished[-1]
      parent.children.append(node)
    return self.unfinished.pop()


class ViewSourceParser(HTMLParser):
  def __init__(self, body):
    super().__init__(body)
    self.source_content = []
  
  def parse(self):
    text = "" 
    in_tag = False
    i = 0

    while i < len(self.body):
      c = self.body[i]

      if c == "<" and i + 3 < len(self.body) and self.body[i:i+4] == "<!--":
        if text and not in_tag:
          self.source_content.append(("text", text))
          text = ""
        end = self.body.find("-->", i + 4)
        if end != -1:
          self.source_content.append(("tag", self.body[i:end+3]))
          i = end + 3
          continue
        else:
          break
      elif c == "<":
        in_tag = True
        if text: 
          # Text content before tag - will be made bold
          self.source_content.append(("text", text))
        text = "<"
      elif c == ">":
        in_tag = False
        text += c
        # Tag content - normal font
        self.source_content.append(("tag", text))
        text = ""
      else:
        text += c
      i += 1
      
    if text:
      if in_tag:
        self.source_content.append(("tag", text))
      else:
        self.source_content.append(("text", text))
    
    return self.create_tree()
  
  def create_tree(self):
    # Create a document tree for view-source mode
    # Wrap everything in <pre> to preserve whitespace and newlines
    html = Element("html", {}, None)
    body = Element("body", {}, html)
    pre = Element("pre", {}, body)
    
    html.children.append(body)
    body.children.append(pre)
    
    for content_type, content in self.source_content:
      if content_type == "text":
        # Text content - wrap in <b> tag for bold
        b_elem = Element("b", {}, pre)
        text_node = Text(content, b_elem)
        b_elem.children.append(text_node)
        pre.children.append(b_elem)
      else:  # "tag"
        # Tag content - normal font, just add as text
        text_node = Text(content, pre)
        pre.children.append(text_node)
    
    return html