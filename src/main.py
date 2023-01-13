import tkinter as tk
import threading
import sys
import logging
from core.common import *
from tkinter.scrolledtext import ScrolledText


class MainPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry('750x575')
        self.parent.resizable(False, False)

        self.preview_canvas = tk.Canvas(self.parent, bg="grey")
        self.colormap_canvas = tk.Canvas(self.parent, bg="grey")

        self.preview_label = tk.Label(self.parent, text="Preview Window")

        self.equation_box = ScrolledText(self.parent)

        self.save_colormap_button = tk.Button(self.parent, bg="grey", command=self.save_colormap,
                                              text="""Save\nColormap""")
        self.load_colormap_button = tk.Button(self.parent, bg="grey", command=self.load_colormap,
                                              text="""Load\nColormap""")
        self.edit_colormap_button = tk.Button(self.parent, bg="grey", command=self.edit_colormap,
                                              text="""Edit\nColormap""")
        self.reset_colormap_button = tk.Button(self.parent, bg="grey", command=self.reset_colormap,
                                               text="""Reset\nColormap""")
        self.edit_vwindow_button = tk.Button(self.parent, bg="grey", command=self.edit_vwin, text="""Edit\nV-Window""")
        self.supersampling_button = tk.Button(self.parent, bg="grey", command=self.supersampling,
                                              text="""Supersampling\nsettings""")
        self.save_project_button = tk.Button(self.parent, bg="grey", command=self.save_project,
                                             text="""Save\nproject""")
        self.load_project_button = tk.Button(self.parent, bg="grey", command=self.load_project,
                                             text="""Load\nproject""")
        self.settings_button = tk.Button(self.parent, bg="grey", command=self.settings,
                                         text="""Settings &\nPreferences""")
        self.parameter_button = tk.Button(self.parent, bg="grey", command=self.parameters, text="""Parameter\nConfig""")

        self.render_button = tk.Button(self.parent, bg="grey", command=self.render, text="Render Project")
        self.video_button = tk.Button(self.parent, bg="grey", command=self.video, text="Video mode settings")

        self.preview_canvas.place(x=8, y=15, height=400, width=400)
        self.colormap_canvas.place(x=428, y=15, height=400, width=60)

        self.preview_label.place(x=8, y=0)

        self.equation_box.place(x=8, y=445, height=120, width=400)

        self.save_colormap_button.place(x=508, y=15, height=60, width=95)
        self.load_colormap_button.place(x=628, y=15, height=60, width=95)
        self.edit_colormap_button.place(x=508, y=100, height=60, width=95)
        self.reset_colormap_button.place(x=628, y=100, height=60, width=95)
        self.edit_vwindow_button.place(x=508, y=188, height=60, width=95)
        self.supersampling_button.place(x=628, y=188, height=60, width=95)
        self.save_project_button.place(x=508, y=273, height=60, width=95)
        self.load_project_button.place(x=628, y=273, height=60, width=95)
        self.settings_button.place(x=508, y=352, height=60, width=95)
        self.parameter_button.place(x=628, y=352, height=60, width=95)

        self.render_button.place(x=428, y=442, width=295, height=50, )
        self.video_button.place(x=428, y=511, width=295, height=50, )

        logging.debug("MainPage initialized")

        logging.debug("Inserting default equations into text box...")
        try:
            default_x = open("defaults/default_eq_x.txt", "r", encoding="utf-8")
            default_y = open("defaults/default_eq_y.txt", "r", encoding="utf-8")

            default_x_text = """""".join(default_x.readlines())
            default_y_text = """""".join(default_y.readlines())
            default_x.close()
            default_y.close()

            default_overall = default_x_text + '\n' + default_y_text
        except Exception as e:
            logging.error("Loading defaults failed, reverting to hardcode backup [x=xt, y=yt]...")
            logging.error(f"Internal error - {e}")
            default_overall = "x=x*t\\x\ny=y*t\\y"

        self.equation_box.insert(tk.END, default_overall)

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
        logging.debug("Trying to open new window...")
        vwin_config_window = tk.Toplevel(self.parent)
        vwin_config_app = VWinConfigWindow(vwin_config_window)

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
        param_app = ParameterSettingsWindow(param_window)

    def render(self):
        logging.debug("User pressed button - 'Render'")

    def video(self):
        logging.debug("User pressed button - 'Video mode settings'")


class PopupWindow:
    def __init__(self, parent, on_close=None):
        self.parent = parent
        self.parent.resizable(False, False)
        self.frame = tk.Frame(self.parent)
        self.on_close = on_close

        self.exit_button = tk.Button(self.parent, bg="grey", text="Save and exit", command=self.exit_window)

    def exit_window(self, *args, **kwargs):
        if self.on_close is not None:
            self.on_close(*args, **kwargs)

        self.parent.destroy()


class ParameterSettingsWindow(PopupWindow):
    def __init__(self, parent):
        super().__init__(parent, on_close=self.save)
        self.parent.geometry("400x200")

        self.temp_text_box = ScrolledText(self.parent)

        self.temp_text_box.place(x=12, y=14, height=120, width=375)
        self.exit_button.place(x=12, y=147, height=45, width=375)

        logging.debug("ParameterSettings window initialized.")

        self.temp_text_box.insert(tk.END, "Todo: parameters backend")

    def save(self):
        logging.debug("Closing ParameterSettings window...")


class VWinConfigWindow(PopupWindow):
    def __init__(self, parent):
        super().__init__(parent, on_close=self.save)
        self.parent.geometry('400x350')

        self.search_window = tk.Button(self.parent, bg="grey", text="Search \n Window", command=self.search_window)
        self.reset = tk.Button(self.parent, bg="grey", text="Reset", command=self.reset)

        self.x_start_label = tk.Label(self.parent, bg="grey", text="X Start")
        self.y_start_label = tk.Label(self.parent, bg="grey", text="Y Start")
        self.x_end_label = tk.Label(self.parent, bg="grey", text="X End")
        self.y_end_label = tk.Label(self.parent, bg="grey", text="Y End")

        self.x_start_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL,
                                       command=self.sliders_updated)
        self.y_start_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL,
                                       command=self.sliders_updated)
        self.x_end_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL,
                                     command=self.sliders_updated)
        self.y_end_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL,
                                     command=self.sliders_updated)

        self.x_start_entry = tk.Entry(self.parent)
        self.y_start_entry = tk.Entry(self.parent)
        self.x_end_entry = tk.Entry(self.parent)
        self.y_end_entry = tk.Entry(self.parent)

        self.x_start_label.place(x=9, y=86, width=70, height=32)
        self.y_start_label.place(x=9, y=139, width=70, height=32)
        self.x_end_label.place(x=9, y=192, width=70, height=32)
        self.y_end_label.place(x=9, y=245, width=70, height=32)

        self.x_start_slider.place(x=104, y=86, width=185, height=32)
        self.y_start_slider.place(x=104, y=139, width=185, height=32)
        self.x_end_slider.place(x=104, y=192, width=185, height=32)
        self.y_end_slider.place(x=104, y=245, width=185, height=32)

        self.x_start_entry.place(x=314, y=86, width=70, height=32)
        self.y_start_entry.place(x=314, y=139, width=70, height=32)
        self.x_end_entry.place(x=314, y=192, width=70, height=32)
        self.y_end_entry.place(x=314, y=245, width=70, height=32)

        self.search_window.place(x=9, y=6, width=170, height=60)
        self.reset.place(x=214, y=6, width=170, height=60)

        self.exit_button.place(x=9, y=299, width=375, height=45)

        logging.debug("VWin Settings window initialised.")

        logging.warning("Need to load values here not just call sliders_updated()")
        
        logging.debug("Updating entries")
        self.sliders_updated()

    def sliders_updated(self, *args):
        logging.debug("Sliders changed - updating text box values")
        self.x_start_entry.delete(0, tk.END)
        self.y_start_entry.delete(0, tk.END)
        self.x_end_entry.delete(0, tk.END)
        self.y_end_entry.delete(0, tk.END)
        self.x_start_entry.insert(tk.END, str(self.x_start_slider.get()))
        self.y_start_entry.insert(tk.END, str(self.y_start_slider.get()))
        self.x_end_entry.insert(tk.END, str(self.x_end_slider.get()))
        self.y_end_entry.insert(tk.END, str(self.y_end_slider.get()))

    def save(self):
        # Needs to pass out all of this
        self.x_start_slider.get()
        self.y_start_slider.get()
        self.x_end_slider  .get()
        self.y_end_slider  .get()

    def search_window(self):
        pass

    def reset(self):
        self.x_start_slider.set(0)
        self.y_start_slider.set(0)
        self.x_end_slider  .set(0)
        self.y_end_slider  .set(0)
        self.sliders_updated()



def main():
    initialise_logger(True)  # change to false during prod
    structure_check(getcwd())
    root = tk.Tk()

    logging.debug("Starting Tk window")

    app = MainPage(root)
    root.mainloop()


if __name__ == '__main__':
    main()
