import tkinter

from browser import Browser
from url import URL

if __name__ == "__main__":
  import sys
  Browser().new_tab(URL(sys.argv[1]))
  tkinter.mainloop()