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
        logging.debug("Trying to open new window...")
        settings_window = tk.Toplevel(self.parent)
        settings_app = SettingsWindow(settings_window)
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
        self.x_end_slider.get()
        self.y_end_slider.get()

    def search_window(self):
        logging.debug("User pressed button - 'Search Window'")
        logging.debug("Trying to open new window...")
        search_window = tk.Toplevel(self.parent)
        search_app = SearchWindow(search_window)

    def reset(self):
        self.x_start_slider.set(0)
        self.y_start_slider.set(0)
        self.x_end_slider.set(0)
        self.y_end_slider.set(0)
        self.sliders_updated()


class SearchWindow(PopupWindow):
    def __init__(self, parent):
        # idk if im happy with the way scale works atm. maybe do it by mouse clicks?
        super().__init__(parent)
        self.parent.geometry('400x350')

        self.search_canvas = tk.Canvas(self.parent, bg="grey")

        self.search_label = tk.Label(self.parent, text="Search Area")
        self.scale_label = tk.Label(self.parent, text="Scale")
        self.x_axis_label = tk.Label(self.parent, text="X Axis")
        self.y_axis_label = tk.Label(self.parent, text="Y Axis")
        self.x_val_label = tk.Label(self.parent, text="X Val: 0")
        self.y_val_label = tk.Label(self.parent, text="Y Val: 0")

        self.scale_slider = tk.Scale(self.parent, from_=1, to=10000, orient=tk.VERTICAL, command=self.scale_changed)

        axis_options = ["x", "y", "p1", "p2"]
        self.x_axis = tk.StringVar()
        self.x_axis.set("x")
        self.x_axis_dropdown = tk.OptionMenu(self.parent, self.x_axis, *axis_options)

        axis_options = ["x", "y", "p1", "p2"]
        self.y_axis = tk.StringVar()
        self.y_axis.set("y")
        self.y_axis_dropdown = tk.OptionMenu(self.parent, self.y_axis, *axis_options)

        self.search_canvas.place(x=9, y=15, width=320, height=200)

        self.search_label.place(x=9, y=0, width=100, height=10)
        self.scale_label.place(x=340, y=0, width=35, height=10)
        self.x_axis_label.place(x=9, y=228, width=40, height=10)
        self.y_axis_label.place(x=9, y=269, width=40, height=10)
        self.x_val_label.place(x=339, y=228, width=60, height=30)
        self.y_val_label.place(x=339, y=269, width=60, height=30)

        self.scale_slider.place(x=339, y=15, height=200, width=50)

        self.x_axis_dropdown.place(x=59, y=224, width=270, height=25)
        self.y_axis_dropdown.place(x=59, y=265, width=270, height=25)

        self.exit_button.place(x=9, y=299, height=45, width=375)

    def scale_changed(self, *args):
        pass

    def mouse_moved_in_canvas(self):
        self.x_val_label['text'] = 1  # this needs to be changed to use the mouse pointer and scaling
        self.y_val_label['text'] = 1  # this needs to be changed to use the mouse pointer and scaling


def update_needed(f):
    def wrapper(*args):
        logging.debug("Update needed for a settings frame...")
        x= f(*args)
        self = args[0]
        logging.debug("Destroying previous widgets in actual settings frame....")
        for widget in self.actual_settings_frame.winfo_children():
            widget.destroy()

        logging.debug("Instantiating new settings class into the actual settings frame")
        self.frame_content(self.actual_settings_frame)
        return x
    return wrapper


class SettingsWindow(PopupWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.geometry('750x450')

        self.bar_callbacks = [self.general, self.rendering, self.files, self.color, self.ui, self.maths, self.update_method]
        self.settings_bar = SettingsBar(parent, self.bar_callbacks)
        self.exit_button.place(x=25, y=395, width=700, height=45)

        self.actual_settings_frame = tk.Frame(self.parent, bg="grey")
        self.actual_settings_frame.place(x=122, y=12, width=616, height=370)

        logging.debug("Trying to render default (general) settings frame...")
        self.frame_content = GeneralSettings
        self.frame_content(self.actual_settings_frame)

    @update_needed
    def general(self):
        logging.debug("User opened general tab of settings")
        self.frame_content = GeneralSettings

    @update_needed
    def rendering(self):
        logging.debug("User opened general tab of settings")
        self.frame_content = RenderingSettings

    @update_needed
    def files(self):
        logging.debug("User opened files tab of settings")
        self.frame_content = FilesSettings

    @update_needed
    def color(self):
        logging.debug("User opened color tab of settings")
        self.frame_content = ColorSettings

    @update_needed
    def ui(self):
        logging.debug("User opened ui tab of settings")
        self.frame_content = UISettings

    @update_needed
    def maths(self):
        logging.debug("User opened maths tab of settings")
        self.frame_content = MathsSettings

    @staticmethod
    def update_method():
        logging.debug("User opened update tab of settings")
        logging.error("Not Implemented")


class GeneralSettings:
    def __init__(self, parent):
        self.parent = parent
        self.test_label = tk.Label(self.parent, text="GENERAL")
        self.test_label.place(x=0, y=10, width=100, height=10)


class RenderingSettings:
    def __init__(self, parent):
        self.parent = parent
        self.test_label = tk.Label(self.parent, text="RENDER")
        self.test_label.place(x=0, y=10, width=100, height=10)


class FilesSettings:
    def __init__(self, parent):
        self.parent = parent
        self.test_label = tk.Label(self.parent, text="FILES")
        self.test_label.place(x=0, y=10, width=100, height=10)


class ColorSettings:
    def __init__(self, parent):
        self.parent = parent
        self.test_label = tk.Label(self.parent, text="COLOR")
        self.test_label.place(x=0, y=10, width=100, height=10)


class UISettings:
    def __init__(self, parent):
        self.parent = parent
        self.test_label = tk.Label(self.parent, text="UI")
        self.test_label.place(x=0, y=10, width=100, height=10)


class MathsSettings:
    def __init__(self, parent):
        self.parent = parent
        self.test_label = tk.Label(self.parent, text="MATHS")
        self.test_label.place(x=0, y=10, width=100, height=10)


class SettingsBar:
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks

        self.general_button = tk.Button(self.parent, bg="grey", command=self.callbacks[0], text="Genera")
        self.rendering_button = tk.Button(self.parent, bg="grey", command=self.callbacks[1], text="Rendering")
        self.files_button = tk.Button(self.parent, bg="grey", command=self.callbacks[2], text="Files")
        self.color_button = tk.Button(self.parent, bg="grey", command=self.callbacks[3], text="Color")
        self.ui_button = tk.Button(self.parent, bg="grey", command=self.callbacks[4], text="UI")
        self.maths_button = tk.Button(self.parent, bg="grey", command=self.callbacks[5], text="Maths")
        self.update_button = tk.Button(self.parent, bg="grey", command=self.callbacks[6], text="Update")
        self.placeholder = tk.Label(self.parent, bg="grey")

        self.general_button.place(x=13, y=12, width=95, height=15)
        self.rendering_button.place(x=13, y=27, width=95, height=15)
        self.files_button.place(x=13, y=42, width=95, height=15)
        self.color_button.place(x=13, y=57, width=95, height=15)
        self.ui_button.place(x=13, y=73, width=95, height=15)
        self.maths_button.place(x=13, y=88, width=95, height=15)
        self.update_button.place(x=13, y=103, width=95, height=15)
        self.placeholder.place(x=13, y=118, width=95, height=265)


def main():
    initialise_logger(True)  # change to false during prod
    structure_check(getcwd())
    root = tk.Tk()

    logging.debug("Starting Tk window")

    app = MainPage(root)
    root.mainloop()


if __name__ == '__main__':
    main()
