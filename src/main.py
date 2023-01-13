import tkinter as tk
import threading
import sys
import logging
from core.common import *


class MainPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry('750x575')
        self.parent.resizable(False, False)

        self.preview_canvas  = tk.Canvas(self.parent, bg="grey")
        self.colormap_canvas = tk.Canvas(self.parent, bg="grey")

        self.preview_label   = tk.Label(self.parent, text="Preview Window")

        self.save_colormap_button    = tk.Button(self.parent, bg="grey", command=self.save_colormap,  text="""Save\nColormap"""         )
        self.load_colormap_button    = tk.Button(self.parent, bg="grey", command=self.load_colormap,  text="""Load\nColormap"""         )
        self.edit_colormap_button    = tk.Button(self.parent, bg="grey", command=self.edit_colormap,  text="""Edit\nColormap"""         )
        self.reset_colormap_button   = tk.Button(self.parent, bg="grey", command=self.reset_colormap, text="""Reset\nColormap"""        )
        self.edit_vwindow_button     = tk.Button(self.parent, bg="grey", command=self.edit_vwin,      text="""Edit\nV-Window"""         )
        self.supersampling_button    = tk.Button(self.parent, bg="grey", command=self.supersampling,  text="""Supersampling\nsettings""")
        self.save_project_button     = tk.Button(self.parent, bg="grey", command=self.save_project,   text="""Save\nproject"""          )
        self.load_project_button     = tk.Button(self.parent, bg="grey", command=self.load_project,   text="""Load\nproject"""          )
        self.settings_button         = tk.Button(self.parent, bg="grey", command=self.settings,       text="""Settings &\nPreferences""")
        self.parameter_button        = tk.Button(self.parent, bg="grey", command=self.parameters,     text="""Parameter\nConfig"""      )

        self.render_button = tk.Button(self.parent,  bg="grey", command=self.render, text="Render Project")
        self.video_button  = tk.Button(self.parent,  bg="grey", command=self.video, text="Video mode settings")

        self.preview_canvas.place(x=8, y=15, height=400, width=400)
        self.colormap_canvas.place(x=428, y=15, height=400, width=60)

        self.preview_label.place(x=8, y=0)

        self.save_colormap_button .place(x=508, y=15,  height=60, width=95)
        self.load_colormap_button .place(x=628, y=15,  height=60, width=95)
        self.edit_colormap_button .place(x=508, y=100, height=60, width=95)
        self.reset_colormap_button.place(x=628, y=100, height=60, width=95)
        self.edit_vwindow_button  .place(x=508, y=188, height=60, width=95)
        self.supersampling_button .place(x=628, y=188, height=60, width=95)
        self.save_project_button  .place(x=508, y=273, height=60, width=95)
        self.load_project_button  .place(x=628, y=273, height=60, width=95)
        self.settings_button      .place(x=508, y=352, height=60, width=95)
        self.parameter_button     .place(x=628, y=352, height=60, width=95)

        self.render_button.place(x=428, y=442, width=295, height=50,)
        self.video_button.place(x=428,  y=511, width=295, height=50,)

        logging.debug("MainPage initialized")

    def save_colormap(self):
        logging.debug("User pressed button - 'Save Colormap'")

    def load_colormap(self):
        logging.debug("User pressed button - 'Load Colormap'")

    def edit_colormap(self):
        logging.debug("User pressed button - 'Edit Colormap'")

    def reset_colormap(self):
        logging.debug("User pressed button - 'Reset Colormap'")

    def edit_vwin(self):
        logging.debug("User pressed button - 'Edit Vwin'")

    def supersampling(self):
        logging.debug("User pressed button - 'Supersampling'")

    def save_project(self):
        logging.debug("User pressed button - 'Save Project'")

    def load_project(self):
        logging.debug("User pressed button - 'Load Project'")

    def settings(self):
        logging.debug("User pressed button - 'Settings'")

    def parameters(self):
        logging.debug("User pressed button - 'Parameters'")
        logging.debug("Trying to open new window...")
        param_window = tk.Toplevel(self.parent)
        param_app = ParameterSettings(param_window)
    def render(self):
        logging.debug("User pressed button - 'Render'")

    def video(self):
        logging.debug("User pressed button - 'Video mode settings'")


class ParameterSettings:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.parent.geometry('400x200')
        self.parent.resizable(False, False)

        #todo: text box
        self.exit_button = tk.Button(self.parent, bg="grey", text="Save and exit", command=self.exit_window)

        self.exit_button.place(x=12, y=147, height=45, width=375)

        logging.debug("ParameterSettings window initalized.")
    def exit_window(self):
        #todo: save here
        logging.debug("Closing ParameterSettings window...")
        self.parent.destroy()
def main():
    initialise_logger(True) #change to false during prod
    structure_check(getcwd())
    root = tk.Tk()

    logging.debug("Starting Tk window")

    app = MainPage(root)
    root.mainloop()


if __name__ == '__main__':
    main()