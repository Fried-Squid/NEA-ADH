import tkinter as tk
import threading
from core import *

class MainPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometery('750x575')
def main():
    structure_check()
    root = tk.Tk()
    app = MainPage(root)
    root.mainloop()
if __name__ == '__main__':
    main()