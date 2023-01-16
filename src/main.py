import threading
import tkinter as tk
from tkinter import colorchooser as cc
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText

from core.common import *


class MainPage(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry('750x575')
        self.parent.resizable(False, False)
        self.x = 1  # temp to make linter be quiet about project save/load being static but not declared as such

        self.colormap = Colormap(None)  # Initialised with None as colormap is loaded straight away
        loaded = self.colormap.load(getcwd() + "/defaults/default.colormap")
        if not loaded:
            logging.critical("Default colormap could not be loaded. Exiting...")
            exit(126)

        self.preview_canvas = tk.Canvas(self.parent, bg="grey")
        self.colormap_canvas = tk.Canvas(self.parent, bg="grey")

        self.preview_label = tk.Label(self.parent, text="Preview Window")

        self.equation_box = ScrolledText(self.parent)

        self.save_colormap_button  = tk.Button(self.parent, bg="grey", command=self.save_colormap,  text="""Save\nColormap""")
        self.load_colormap_button  = tk.Button(self.parent, bg="grey", command=self.load_colormap,  text="""Load\nColormap""")
        self.edit_colormap_button  = tk.Button(self.parent, bg="grey", command=self.edit_colormap,  text="""Edit\nColormap""")
        self.reset_colormap_button = tk.Button(self.parent, bg="grey", command=self.reset_colormap, text="""Reset\nColormap""")
        self.edit_vwindow_button   = tk.Button(self.parent, bg="grey", command=self.edit_vwin,      text="""Edit\nV-Window""")
        self.supersampling_button  = tk.Button(self.parent, bg="grey", command=self.supersampling,  text="""Supersampling\nsettings""")
        self.save_project_button   = tk.Button(self.parent, bg="grey", command=self.save_project,   text="""Save\nproject""")
        self.load_project_button   = tk.Button(self.parent, bg="grey", command=self.load_project,   text="""Load\nproject""")
        self.settings_button       = tk.Button(self.parent, bg="grey", command=self.settings,       text="""Settings &\nPreferences""")
        self.parameter_button     = tk.Button(self.parent, bg="grey", command=self.parameters,      text="""Parameter\nConfig""")

        self.render_button = tk.Button(self.parent, bg="grey", command=self.render, text="Render Project")
        self.video_button  = tk.Button(self.parent, bg="grey", command=self.video,  text="Video mode settings")

        self.preview_canvas.place(x=8, y=15, height=400, width=400)
        self.colormap_canvas.place(x=428, y=15, height=400, width=60)

        self.preview_label.place(x=8, y=0)

        self.equation_box.place(x=8, y=445, height=120, width=400)

        self.save_colormap_button   .place(x=508, y=15,  height=60, width=95)
        self.load_colormap_button   .place(x=628, y=15,  height=60, width=95)
        self.edit_colormap_button   .place(x=508, y=100, height=60, width=95)
        self.reset_colormap_button  .place(x=628, y=100, height=60, width=95)
        self.edit_vwindow_button    .place(x=508, y=188, height=60, width=95)
        self.supersampling_button   .place(x=628, y=188, height=60, width=95)
        self.save_project_button    .place(x=508, y=273, height=60, width=95)
        self.load_project_button    .place(x=628, y=273, height=60, width=95)

        self.settings_button    .place(x=508, y=352, height=60, width=95)
        self.parameter_button   .place(x=628, y=352, height=60, width=95)

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
        self.update_colormap_canvas()

        self.func = lambda: None
        self.parse_eqs()

        self.start_pos = [0, 0]
        self.tail_end = 1

        self.settings = Settings(self.colormap)
        self.camera   = Camera(0, 0, 0, (1,1), 10)
        self.attractor = Attractor([Emitter(self.func, self.start_pos, self.tail_end)], [], self.camera, self.settings, self.preview_canvas)



    def update_colormap_canvas(self):
        t = threading.Thread(target=display_colormap_on_canvas, args=(self.colormap_canvas, self.colormap, 60, 400))
        t.start()

    def update_preview_canvas(self):
        pass

    def parse_eqs(self):
        rawtext = self.equation_box.get(0, tk.END)
        self.func = parse_eq(rawtext)

    def save_colormap(self):
        logging.debug("User pressed button - 'Save Colormap'")
        filename = fd.asksaveasfilename(filetypes=[("Colormap File", "*.colormap"),("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute save path is {filename}")
        self.colormap.save(filename.rstrip(".colormap"))

    def load_colormap(self):
        logging.debug("User pressed button - 'Load Colormap'")
        filename = fd.askopenfilename(filetypes=[("Colormap File", "*.colormap"),("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute filepath opened is {filename}")
        self.colormap.load(filename)

    def edit_colormap(self):
        logging.debug("User pressed button - 'Edit Colormap'")
        logging.debug("Trying to open new window...")
        colormap_editor_window = tk.Toplevel(self.parent)
        colormap_editor_app = ColormapEditor(colormap_editor_window, self.colormap, self.set_colormap)

    def reset_colormap(self):
        logging.debug("User pressed button - 'Reset Colormap'")
        loaded = self.colormap.load(getcwd() + "/defaults/default.colormap")
        if not loaded:
            logging.error("Default colormap could not be loaded - reset failed.")
        self.update_colormap_canvas()
    def edit_vwin(self):
        logging.debug("User pressed button - 'Edit Vwin'")
        logging.debug("Trying to open new window...")
        vwin_config_window = tk.Toplevel(self.parent)
        vwin_config_app = VWinConfigWindow(vwin_config_window)

    def supersampling(self):
        logging.debug("User pressed button - 'Supersampling'")
        logging.debug("Trying to open new window...")
        supersampling_config_window = tk.Toplevel(self.parent)
        supersampling_config_app = SupersamplingWindow(supersampling_config_window, self.attractor)

    def save_project(self):
        logging.debug("User pressed button - 'Save Project'")
        filename = fd.asksaveasfilename(filetypes=[("Project File", "*.proj"),("Raw Text Project", "*.txt")], defaultextension=".proj")
        logging.debug(f"Absolute save path is {filename}")
        self.x=1

    def load_project(self):
        logging.debug("User pressed button - 'Load Project'")
        filename = fd.askopenfilename(filetypes=[("Project File", "*.proj"),("Raw Text Project", "*.txt")], defaultextension=".proj")
        logging.debug(f"Absolute filepath opened is {filename}")
        self.x = 1

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
        self.x = 1
        # self.attractor.render(self.settings.resolution, self.settings.extension)

    @staticmethod
    def video(self):
        logging.debug("User pressed button - 'Video mode settings'")
        logging.error("Not yet implemented")

    def set_colormap(self, colormap: Colormap):
        self.colormap = colormap
        self.update_colormap_canvas()


#talk about using this parent class in design
class PopupWindow:
    def __init__(self, parent, on_close=None):
        self.parent = parent
        self.parent.resizable(False, False)
        self.frame = tk.Frame(self.parent)
        self.on_close = on_close

        self.exit_button = tk.Button(self.parent, bg="grey", text="Save and exit", command=self.exit_window)

    def exit_window(self, *args, **kwargs):
        if self.on_close is not None:
            self.on_close(*args, **kwargs) #talk about arg passing in design

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

        self.x_start_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.sliders_updated)
        self.y_start_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.sliders_updated)
        self.x_end_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.sliders_updated)
        self.y_end_slider = tk.Scale(self.parent, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.sliders_updated)

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


def update_needed_settings(f):
    def wrapper(*args): #talk about writing this algorithm as a wrapper
        logging.debug("Update needed for a settings frame...")
        x= f(*args)
        self = args[0]
        logging.debug("Destroying previous widgets in actual settings frame....")
        for widget in self.actual_settings_frame.winfo_children():
            widget.destroy()

        logging.debug("Instantiating new settings class into the actual settings frame")
        self.frame_content(self.actual_settings_frame)
        return x
    return wrapper # talk about the None error you had from returning this


class SettingsWindow(PopupWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.geometry('750x450')

        self.bar_callbacks = [self.general, self.rendering, self.files, self.color, self.ui, self.maths, self.update_method] #talk about the callbacks in development
        self.settings_bar = SettingsBar(parent, self.bar_callbacks)
        self.exit_button.place(x=25, y=395, width=700, height=45)

        self.actual_settings_frame = tk.Frame(self.parent, bg="grey")
        self.actual_settings_frame.place(x=122, y=12, width=616, height=370)

        logging.debug("Trying to render default (general) settings frame...") #talk about these algos in design
        self.frame_content = GeneralSettings
        self.frame_content(self.actual_settings_frame)

    @update_needed_settings
    def general(self):
        logging.debug("User opened general tab of settings")
        self.frame_content = GeneralSettings

    @update_needed_settings
    def rendering(self):
        logging.debug("User opened general tab of settings")
        self.frame_content = RenderingSettings

    @update_needed_settings
    def files(self):
        logging.debug("User opened files tab of settings")
        self.frame_content = FilesSettings

    @update_needed_settings
    def color(self):
        logging.debug("User opened color tab of settings")
        self.frame_content = ColorSettings

    @update_needed_settings
    def ui(self):
        logging.debug("User opened ui tab of settings")
        self.frame_content = UISettings

    @update_needed_settings
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


# talk about window design change while coding because it felt off during testing
def updated_needed_colormap(f):
    def wrapper(*args): #talk about writing this algorithm as a wrapper
        logging.debug("Update needed for a colormap window...")
        x= f(*args)
        self = args[0]
        self.update_colormap()
        self.update_button()
        return x
    return wrapper  # talk about the None error you had from returning this


class ColormapEditor(PopupWindow):
    def __init__(self, parent, colormap: Colormap, save_callback: Callable):
        super().__init__(parent, on_close=self.save_and_close)
        self.colormap = colormap
        self.save_callback = save_callback
        self.parent = parent
        self.parent.geometry("650x400")

        self.colormap_canvas = tk.Canvas(self.parent, bg="white")

        self.position_slider = tk.Scale(self.parent, from_=0, to=100, orient=tk.VERTICAL, command=self.update_button)

        self.color_button      = tk.Button(self.parent, bg=self.colormap.get_value(int(self.position_slider.get())).hex())  # this required updating common:color, write about
        self.insert_button     = tk.Button(self.parent, bg="grey", text="Insert new\ncolor",             command=self.insert)
        self.delete_button     = tk.Button(self.parent, bg="grey", text="Delete color\nat position",     command=self.delete)
        self.jump_next_button  = tk.Button(self.parent, bg="grey", text="Jump to\nnext color",           command=self.jump_next)
        self.reverse_button    = tk.Button(self.parent, bg="grey", text="Reverse\nColormap",             command=self.reverse)
        self.invert_button     = tk.Button(self.parent, bg="grey", text="Invert\nColors",                command=self.invert)
        self.jump_prev_button  = tk.Button(self.parent, bg="grey", text="Jump to\nprevious color",       command=self.jump_prev)
        self.adjoin_button     = tk.Button(self.parent, bg="grey", text="Adjoin Colormap\nfrom file",    command=self.adjoin)
        self.double_button     = tk.Button(self.parent, bg="grey", text="Compress and\ndouble colormap", command=self.double)
        self.jump_first_button = tk.Button(self.parent, bg="grey", text="Jump to\nfirst color",          command=self.jump_first)
        self.save_button       = tk.Button(self.parent, bg="grey", text="Save\nColormap",                command=self.save)
        self.load_button       = tk.Button(self.parent, bg="grey", text="Load New\nColormap",            command=self.load)
        self.jump_last_button  = tk.Button(self.parent, bg="grey", text="Jump to\nlast color",           command=self.jump_last)

        self.colormap_canvas.place(x=12, y=12, width=60, height=380)

        self.position_slider.place(x=81, y=12, width=40, height=380)

        self.color_button     .place(x=135, y=10,  width=30,  height=380)
        self.insert_button    .place(x=179, y=12,  width=145, height=60)
        self.delete_button    .place(x=338, y=12,  width=145, height=60)
        self.jump_next_button .place(x=496, y=12,  width=145, height=60)
        self.reverse_button   .place(x=179, y=95,  width=145, height=60)
        self.invert_button    .place(x=338, y=95,  width=145, height=60)
        self.jump_prev_button .place(x=496, y=95,  width=145, height=60)
        self.adjoin_button    .place(x=179, y=178, width=145, height=60)
        self.double_button    .place(x=338, y=178, width=145, height=60)
        self.jump_first_button.place(x=496, y=178, width=145, height=60)
        self.save_button      .place(x=179, y=261, width=145, height=60)
        self.load_button      .place(x=338, y=261, width=145, height=60)
        self.jump_last_button .place(x=496, y=261, width=145, height=60)

        self.exit_button.place(x=179, y=345, width=462, height=45)

        self.update_colormap()

    def update_button(self, *args):
        self.color_button.configure(bg=self.colormap.get_value(int(self.position_slider.get())).hex())

    def update_colormap(self):
        t = threading.Thread(target=display_colormap_on_canvas, args=(self.colormap_canvas, self.colormap, 60, 380))
        t.start()

    def color(self):
        pass  # why?

    @updated_needed_colormap
    def insert(self):  # required new method
        output = cc.askcolor()[0]
        color = Color(*output, 255)
        self.colormap.insert_value(color, int(self.position_slider.get()))

    @updated_needed_colormap
    def delete(self):
        currentpos = self.position_slider.get()
        poslist = list(map(lambda x: x[1], self.colormap.get_gradient().__getattribute__("_color_peaks")))
        if currentpos in poslist:
            x = self.colormap.__getattribute__("_gradient").__getattribute__("_color_peaks")
            x.pop(poslist.index(currentpos))
            self.colormap = Colormap(Gradient(x))

    @updated_needed_colormap
    def jump_next(self):
        currentpos = self.position_slider.get()
        poslist = list(map(lambda x:x[1], self.colormap.get_gradient().__getattribute__("_color_peaks")))
        for index, val in enumerate(poslist):
            if val > currentpos:
                self.position_slider.set(poslist[index])
                return

    @updated_needed_colormap
    def invert(self):  # need a new method
        self.colormap.invert()

    @updated_needed_colormap
    def jump_prev(self):
        currentpos = self.position_slider.get()
        poslist = list(map(lambda x: x[1], self.colormap.get_gradient().__getattribute__("_color_peaks")))
        if currentpos == 100:
            self.position_slider.set(poslist[-2])
            return
        for index, val in enumerate(poslist):
            if val > currentpos:
                if poslist[index-1] == currentpos:
                    self.position_slider.set(poslist[index-2])
                else:
                    self.position_slider.set(poslist[index - 1])
                return

    @updated_needed_colormap
    def adjoin(self):
        logging.debug("User pressed button - 'Load Colormap'")
        filename = fd.askopenfilename(filetypes=[("Colormap File", "*.colormap"), ("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute filepath opened is {filename}")
        other_cmp = Colormap(None)  # None initialization is fine here as colormap is loaded
        other_cmp.load(filename)
        self.colormap += other_cmp
        self.colormap *= 100/len(self.colormap)

    @updated_needed_colormap
    def double(self):  # warraneted loads of common updates, added __stuff__ and had to change add logic to add the +1
        self.colormap = self.colormap + self.colormap
        self.colormap = self.colormap*0.5

    @updated_needed_colormap
    def jump_first(self):
        self.position_slider.set(self.colormap.get_gradient().__getattribute__("_color_peaks")[0][1])     # protected access could be an issue

    def save(self):
        logging.debug("User pressed button - 'Save'")
        filename = fd.asksaveasfilename(filetypes=[("Colormap File", "*.colormap"),("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute save path is {filename}")
        self.colormap.save(filename.rstrip(".colormap"))

    def load(self):
        logging.debug("User pressed button - 'Load Colormap'")
        filename = fd.askopenfilename(filetypes=[("Colormap File", "*.colormap"),("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute filepath opened is {filename}")
        self.colormap.load(filename)

    @updated_needed_colormap
    def jump_last(self):
        self.position_slider.set(self.colormap.get_gradient().__getattribute__("_color_peaks")[-1][1])

    @updated_needed_colormap
    def reverse(self):  # needed a new method
        self.colormap = reversed(self.colormap)

    def save_and_close(self, *args, **kwargs):
        self.parent.destroy()
        self.save_callback(self.colormap)


class SupersamplingWindow(PopupWindow):
    def __init__(self, parent, attractor):
        super().__init__(parent)
        self.parent = parent
        self.parent.geometry("400x300")
        self.attractor = attractor
        self.enabled = 1  # self.attractor.supersampling_enabled

        self.algo_label     = tk.Label(self.parent, bg="grey", text="Sampling\nAlgorithm")
        self.x_res_label    = tk.Label(self.parent, bg="grey", text="X\nRes")
        self.y_res_label    = tk.Label(self.parent, bg="grey", text="Y\nRes")

        self.x_res_slider   = tk.Scale(self.parent, orient=tk.HORIZONTAL, from_=128, to=4096)
        self.y_res_slider   = tk.Scale(self.parent, orient=tk.HORIZONTAL, from_=128, to=4096)
        self.x_res_slider.set(1920)
        self.y_res_slider.set(1080)

        algo_options = ["Poisson-disc", "Quincux", "Grid", "Rotated Grid"]
        self.algo = tk.StringVar()
        self.algo.set("Poisson-disc")
        self.algo_dropdown = tk.OptionMenu(self.parent, self.algo, *algo_options)

        self.enable_button  = tk.Button(self.parent, bg="grey", text="Enable Supersampling", command=self.enable)
        self.reset_button   = tk.Button(self.parent, bg="grey", text="Reset to default", command=self.reset)

        self.algo_label    .place(x=12, y=20, width=58, height=32)
        self.x_res_label   .place(x=12, y=66, width=58, height=32)
        self.y_res_label   .place(x=12, y=112, width=58, height=32)

        self.x_res_slider  .place(x=75, y=66, width=311, height=32)
        self.y_res_slider  .place(x=75, y=112, width=311, height=32)

        self.algo_dropdown.place(x=75, y=20, width=311, height=32)

        self.enable_button .place(x=12, y=167, width=170,height=60)
        self.reset_button  .place(x=217, y=167, width=170, height=60)
        self.exit_button   .place(x=12, y=242, width=375, height=45)

    def enable(self):
        self.enabled = (1, 0)[self.enabled]

    def reset(self):
        pass # todo: default settings load here
def main():
    initialise_logger(True)  # change to false during prod
    structure_check(getcwd())
    root = tk.Tk()

    logging.debug("Starting Tk window")

    app = MainPage(root)
    root.mainloop()


if __name__ == '__main__':
    main()
