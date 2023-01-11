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

        self.preview_canvas  = tk.Canvas(self.parent, bg="grey")
        self.colormap_canvas = tk.Canvas(self.parent, bg="grey")

        self.preview_label   = tk.Label(self.parent, text="Preview Window")

        self.save_colormap_button    = tk.Button(self.parent, bg="grey", text="""Save\nColormap""")
        self.load_colormap_button    = tk.Button(self.parent, bg="grey", text="""Load\nColormap""")
        self.edit_colormap_button    = tk.Button(self.parent, bg="grey", text="""Edit\nColormap""")
        self.reset_colormap_button   = tk.Button(self.parent, bg="grey", text="""Reset\nColormap""")
        self.edit_vwindow_button     = tk.Button(self.parent, bg="grey", text="""Edit\nV-Window""")
        self.supersampling_button    = tk.Button(self.parent, bg="grey", text="""Supersampling\nsettings""")
        self.save_project_button     = tk.Button(self.parent, bg="grey", text="""Save\nproject""")
        self.load_project_button     = tk.Button(self.parent, bg="grey", text="""Load\nproject""")
        self.settings_button         = tk.Button(self.parent, bg="grey", text="""Settings &\nPreferences""")
        self.parameter_button        = tk.Button(self.parent, bg="grey", text="""Parameter\nConfig""")

        self.render_button = tk.Button(self.parent,  bg="grey",text="Render Project")
        self.video_button  = tk.Button(self.parent,  bg="grey",text="Video mode settings")

        self.preview_canvas.place(x=8, y=15, height=400, width=400)
        self.colormap_canvas.place(x=428, y=15, height=400, width=60 )

        self.preview_label.place(x=8, y=0)

        self.save_colormap_button .place(x=508, y=15 , height=60, width=95)
        self.load_colormap_button .place(x=628, y=15 , height=60, width=95)
        self.edit_colormap_button .place(x=508, y=100, height=60, width=95)
        self.reset_colormap_button.place(x=628, y=100, height=60, width=95)
        self.edit_vwindow_button  .place(x=508, y=188, height=60, width=95)
        self.supersampling_button .place(x=628, y=188, height=60, width=95)
        self.save_project_button  .place(x=508, y=273, height=60, width=95)
        self.load_project_button  .place(x=628, y=273, height=60, width=95)
        self.settings_button      .place(x=508, y=352, height=60, width=95)
        self.parameter_button     .place(x=628, y=352, height=60, width=95)

        self.render_button.place(x=428, y=442, width=295, height=50,)
        self.video_button.place(x=428, y=511 , width=295, height=50,)

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