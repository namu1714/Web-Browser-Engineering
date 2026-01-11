HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100

def tree_to_list(tree, list):
  list.append(tree)
  for child in tree.children:
    tree_to_list(child, list)
  return list
