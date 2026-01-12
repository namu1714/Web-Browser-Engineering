from parser import Element

INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}

class CSSParser:
  def __init__(self, s):
    self.s = s
    self.i = 0

  def parse(self):
    rules = []
    while self.i < len(self.s):
      try:
        self.whitespace()
        selector = self.selector()
        self.whitespace()
        self.literal("{")
        self.whitespace()
        body = self.body()
        self.whitespace()
        self.literal("}")
        rules.append((selector, body))
      except Exception:
        why = self.ignore_until(["}"])
        if why == "}":
          self.literal("}")
          self.whitespace()
        else:
          break
    return rules
  
  def body(self):
    pairs = {}
    while self.i < len(self.s) and self.s[self.i] != "}":
      try:
        prop, val, important = self.pair()
        # Store both value and importance
        pairs[prop.casefold()] = {"value": val, "important": important}
        self.whitespace()
        self.literal(";")
        self.whitespace()
      except Exception:
        why = self.ignore_until([";", "}"])
        if why == ";":
          self.literal(";")
          self.whitespace()
        else:
          break
    return pairs

  def pair(self):
    prop = self.word()
    self.whitespace()
    self.literal(":")
    self.whitespace()
    val = self.word()

    # Check for !important
    important = False
    saved_pos = self.i
    self.whitespace()
    try:
      if self.i < len(self.s) and self.s[self.i:self.i+1] == "!":
        self.literal("!")
        self.whitespace()
        importance_keyword = self.word()
        if importance_keyword.casefold() == "important":
          important = True
        else:
          # Not !important, restore position
          self.i = saved_pos
      else:
        self.i = saved_pos
    except:
      # Failed to parse !important, restore position
      self.i = saved_pos

    return prop.casefold(), val, important
  
  def selector(self):
    out = TagSelector(self.word().casefold())
    self.whitespace()
    while self.i < len(self.s) and self.s[self.i] != "{":
      tag = self.word()
      descendant = TagSelector(tag.casefold())
      out = DescendantSelector(out, descendant)
      self.whitespace()
    return out
    
  def ignore_until(self, chars):
    while self.i < len(self.s):
      if self.s[self.i] in chars:
        return self.s[self.i]
      else:
        self.i += 1
    return None
  
  def whitespace(self):
    while self.i < len(self.s) and self.s[self.i].isspace():
      self.i += 1
  
  def word(self):
    start = self.i
    while self.i < len(self.s):
      if self.s[self.i].isalnum() or self.s[self.i] in "#-.%!":
        self.i += 1
      else:
        break
    if not (self.i > start):
      raise Exception("Parsing error")
    return self.s[start:self.i]
  
  def literal(self, literal):
    if not (self.i < len(self.s) and self.s[self.i] == literal):
      raise Exception("Parsing error")
    self.i += 1
  

class TagSelector:
  def __init__(self, tag):
    self.tag = tag
    self.priority = 1

  def matches(self, node):
    return isinstance(node, Element) and node.tag == self.tag
  
class DescendantSelector:
  def __init__(self, ancestor, descendant):
    self.ancestor = ancestor
    self.descendant = descendant
    self.priority = ancestor.priority + descendant.priority

  def matches(self, node):
    if not self.descendant.matches(node):
      return False
    while node.parent:
      if self.ancestor.matches(node.parent):
        return True
      node = node.parent
    return False

def style(node, rules):
  node.style = {}
  # Track priority for each property
  style_priorities = {}

  # Helper function to set style property with priority check
  def set_style_property(property, value, priority, important=False):
    if important:
      priority += 1000

    if property not in style_priorities or priority >= style_priorities[property]:
      node.style[property] = value
      style_priorities[property] = priority

  # 1. Apply inherited properties (priority 0)
  for property, default_value in INHERITED_PROPERTIES.items():
    if node.parent:
      set_style_property(property, node.parent.style[property], 0)
    else:
      set_style_property(property, default_value, 0)

  # 2. Apply external CSS rules (priority = selector priority)
  for selector, body in rules:
    if not selector.matches(node):
      continue
    for property, prop_info in body.items():
      # Handle new structure: {"value": val, "important": important}
      if isinstance(prop_info, dict):
        value = prop_info["value"]
        important = prop_info["important"]
      else:
        # Backward compatibility for old structure
        value = prop_info
        important = False
      set_style_property(property, value, selector.priority, important)

  # 3. Apply inline styles (priority 1000)
  if isinstance(node, Element) and "style" in node.attributes:
    pairs = CSSParser(node.attributes["style"]).body()
    for property, prop_info in pairs.items():
      if isinstance(prop_info, dict):
        value = prop_info["value"]
        important = prop_info["important"]
      else:
        # Backward compatibility
        value = prop_info
        important = False
      set_style_property(property, value, 1000, important)

  # 4. Process font-size percentages
  if node.style["font-size"].endswith("%"):
    if node.parent:
      parent_font_size = node.parent.style["font-size"]
    else:
      parent_font_size = INHERITED_PROPERTIES["font-size"]
    node_pct = float(node.style["font-size"][:-1]) / 100
    parent_px = float(parent_font_size[:-2])
    node.style["font-size"] = str(node_pct * parent_px) + "px"

  # 5. Apply to children
  for child in node.children:
    style(child, rules)

def cascade_priority(rule):
  selector, body = rule
  return selector.priority
