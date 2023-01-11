import tkinter as tk
import threading
import sys
import logging
sys.path.insert(1, "core")
from common import *

class MainPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometery('750x575')
        logging.debug("MainPage initialized")


def main():
    initialize_logging()
    structure_check("")
    root = tk.Tk()

    logging.debug("Starting Tk window")

    app = MainPage(root)
    root.mainloop()
if __name__ == '__main__':
    main()