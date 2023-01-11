import tkinter as tk
import threading
import sys
import logging
from os import getcwd
from core.common import *

class MainPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry('750x575')

        logging.debug("MainPage initialized")


def main():
    initialise_logger(True) #change to false during prod
    structure_check(getcwd())
    root = tk.Tk()

    logging.debug("Starting Tk window")

    app = MainPage(root)
    root.mainloop()
if __name__ == '__main__':
    main()