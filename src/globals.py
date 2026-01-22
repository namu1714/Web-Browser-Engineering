HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

def tree_to_list(tree, list):
  list.append(tree)
  for child in tree.children:
    tree_to_list(child, list)
  return list

class Rect:
  def __init__(self, left, top, right, bottom):
    self.left = left
    self.top = top
    self.right = right
    self.bottom = bottom
    
  def containsPoint(self, x, y):
    return x >= self.left and x < self.right \
        and y >= self.top and y < self.bottom
