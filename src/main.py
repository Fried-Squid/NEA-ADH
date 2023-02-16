import threading
import tkinter as tk
from tkinter import colorchooser as cc
from tkinter import filedialog as fd
from tkinter.scrolledtext import ScrolledText
from core.common import *

def updates_settings_frame(f):
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


# talk about window design change while coding because it felt off during testing
def updates_colormap_preview(f):
    def wrapper(*args):  # talk about writing this algorithm as a wrapper
        logging.debug("Update needed for a colormap canvas...")
        x= f(*args)
        self = args[0]
        self.update_colormap()
        try:
            self.update_button()
        except:
            pass  # only needs to execute if there is an update button method, might be a better way to do this?
        return x
    return wrapper  # talk about the None error you had from returning this


def updates_preview(f):
    def wrapper(*args):
        logging.debug("Update needed for a preview canvas...")
        x = f(*args)
        self = args[0]
        self.start_preview_render_thread()
        return x
    return wrapper


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

        self.preview_canvas = tk.Canvas(self.parent, bg="white")
        self.colormap_canvas = tk.Canvas(self.parent)

        self.preview_label = tk.Label(self.parent, text="Preview Window")

        self.equation_box = ScrolledText(self.parent)

        self.save_colormap_button  = tk.Button(self.parent, command=self.save_colormap,  text="""Save\nColormap""")
        self.load_colormap_button  = tk.Button(self.parent, command=self.load_colormap,  text="""Load\nColormap""")
        self.edit_colormap_button  = tk.Button(self.parent, command=self.edit_colormap,  text="""Edit\nColormap""")
        self.reset_colormap_button = tk.Button(self.parent, command=self.reset_colormap, text="""Reset\nColormap""")
        self.edit_vwindow_button   = tk.Button(self.parent, command=self.edit_vwin,      text="""Edit\nV-Window""")
        self.supersampling_button  = tk.Button(self.parent, command=self.supersampling,  text="""Supersampling\nsettings""")
        self.save_project_button   = tk.Button(self.parent, command=self.save_project,   text="""Save\nproject""")
        self.load_project_button   = tk.Button(self.parent, command=self.load_project,   text="""Load\nproject""")
        self.settings_button       = tk.Button(self.parent, command=self.settings,       text="""Settings &\nPreferences""")
        self.parameter_button     = tk.Button(self.parent, command=self.parameters,      text="""Parameter\nConfig""")

        self.render_button = tk.Button(self.parent, command=self.render, text="Render Project")
        self.video_button  = tk.Button(self.parent, command=self.video,  text="Video mode settings")

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
            default = open("defaults/default_eq.txt", "r", encoding="utf-8")

            default_text = """""".join(default.readlines())
            default.close()

        except Exception as e:
            logging.error("Loading defaults failed, reverting to hardcode backup [x=xt, y=yt]...")
            logging.error(f"Internal error - {e}")
            default_overall = "x=x*t\\x\ny=y*t\\y"

        self.equation_box.insert(tk.END, default_text)
        self.update_colormap()

        self.start_pos = [0.1, 0.1]
        self.tail_end = 1

        self.settings = Settings(self.colormap)
        self.cam_rotation = 0

        self.vwin_params = None
        self.attractor = None
        self.preview_render_thread = None
        self.func = None
        self.rendering = False

        self.default_param_value = 1
        self.params = None
        self.params_dict = None

        self.camera = Camera([-2, 2], [2, -2], self.cam_rotation)
        self.parse_eqs()
        self.vwin_save_callback(-2, -2, 2, 2)

        self.equation_box_change_listener()

    def equation_box_change_listener(self):
        t = TextChangeListener(self.equation_box, self.parse_eqs)
        t.start()

    def update_colormap(self):
        t = threading.Thread(target=display_colormap_on_canvas, args=(self.colormap_canvas, self.colormap, 60, 400))
        t.run()
        self.start_preview_render_thread()

    def start_preview_render_thread(self):
        try:
            self.stop_preview_render_thread()
            self.preview_render_thread = self.attractor.async_render([400, 400], self.preview_canvas)
            self.preview_render_thread.start()
        except AttributeError:
            logging.warning("Start render thread called unsafely")

    def stop_preview_render_thread(self):
        if self.preview_render_thread is not None:
            self.preview_render_thread.stop()
            del self.preview_render_thread

    @updates_preview
    def parse_eqs(self):
        rawtext = self.equation_box.get("1.0", tk.END)
        self.params, self.func = parse_eq(rawtext)
        self.params_dict = self.process_new_params()
        del self.attractor
        self.attractor = Attractor([Emitter(self.func, self.params_dict, self.start_pos, self.tail_end)], [], self.camera, self.settings)

    def save_colormap(self):
        logging.debug("User pressed button - 'Save Colormap'")
        filename = fd.asksaveasfilename(filetypes=[("Colormap File", "*.colormap"),("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute save path is {filename}")
        self.colormap.save(filename.rstrip(".colormap"))

    def load_colormap(self):
        logging.debug("User pressed button - 'Load Colormap'")
        filename = fd.askopenfilename(filetypes=[("Colormap File", "*.colormap"),("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute filepath opened is {filename}")
        temp_colormap = Colormap(Gradient([]))
        temp_colormap.load(filename)
        self.set_colormap(temp_colormap)

    def edit_colormap(self):
        logging.debug("User pressed button - 'Edit Colormap'")
        logging.debug("Trying to open new window...")
        colormap_editor_window = tk.Toplevel(self.parent)
        colormap_editor_app = ColormapEditor(colormap_editor_window, self.colormap, self.set_colormap)

    @updates_colormap_preview
    def reset_colormap(self):
        logging.debug("User pressed button - 'Reset Colormap'")
        temp_colormap = Colormap(Gradient([]))
        loaded = temp_colormap.load(getcwd() + "/defaults/default.colormap")
        if not loaded:
            logging.error("Default colormap could not be loaded - reset failed.")
        else:
            self.set_colormap(temp_colormap)

    @updates_preview
    def vwin_save_callback(self, xs, ys, xe, ye):
        self.vwin_params = xs, ys, xe, ye
        self.camera = Camera([xs, ye], [xe, ys], self.cam_rotation)
        del self.attractor
        self.attractor = Attractor([Emitter(self.func, self.params_dict, self.start_pos, self.tail_end)], [], self.camera, self.settings)

    def edit_vwin(self):
        logging.debug("User pressed button - 'Edit Vwin'")
        logging.debug("Trying to open new window...")
        vwin_config_window = tk.Toplevel(self.parent)
        vwin_config_app = VWinConfigWindow(vwin_config_window, self.vwin_save_callback)

    def supersampling(self):
        logging.debug("User pressed button - 'Supersampling'")
        logging.debug("Trying to open new window...")
        supersampling_config_window = tk.Toplevel(self.parent)
        supersampling_config_app = SupersamplingWindow(supersampling_config_window, self.attractor)

    def save_project(self):
        logging.debug("User pressed button - 'Save Project'")
        filename = fd.asksaveasfilename(filetypes=[("Project File", "*.proj"),("Raw Text Project", "*.txt")], defaultextension=".proj")
        logging.debug(f"Absolute save path is {filename}")
        self.x = 1

    @updates_colormap_preview
    def load_project(self):
        logging.debug("User pressed button - 'Load Project'")
        filename = fd.askopenfilename(filetypes=[("Project File", "*.proj"),("Raw Text Project", "*.txt")], defaultextension=".proj")
        logging.debug(f"Absolute filepath opened is {filename}")
        self.x = 1

    @updates_preview
    def settings(self):
        logging.debug("User pressed button - 'Settings'")
        logging.debug("Trying to open new window...")
        settings_window = tk.Toplevel(self.parent)
        settings_app = SettingsWindow(settings_window)

    def parameters(self):
        logging.debug("User pressed button - 'Parameters'")
        logging.debug("Trying to open new window...")
        param_window = tk.Toplevel(self.parent)
        param_app = ParameterSettingsWindow(param_window, self.params, self.params_save_callback, existing_params = self.params_dict)

    @updates_preview
    def params_save_callback(self, params_dict: dict):
        self.params_dict = params_dict
        del self.attractor
        self.attractor = Attractor([Emitter(self.func, self.params_dict, self.start_pos, self.tail_end)], [], self.camera, self.settings)

    @updates_preview
    def process_new_params(self):
        old_params = self.params_dict
        if old_params is None:
            old_params = {}
        new_param_keys = []
        new_param_vals = []
        for param in self.params:
            new_param_keys.append(param)
            try:
                new_param_vals.append(old_params[param])
            except KeyError:
                new_param_vals.append(self.default_param_value)
        new = dict(zip(new_param_keys, new_param_vals))
        return new

    def render(self):
        logging.debug("User pressed button - 'Render'")
        self.x = 1
        self.parse_eqs()
        # temp to test previous
        progress_bar_window = tk.Toplevel(self.parent)
        progress_bar_app = RenderBar(progress_bar_window, self.attractor)
        progress_bar_app.start()

    @staticmethod
    def video(self):
        logging.debug("User pressed button - 'Video mode settings'")
        logging.error("Not yet implemented")

    @updates_colormap_preview
    def set_colormap(self, colormap: Colormap):
        self.colormap = colormap
        self.settings.colormap = colormap
        del self.attractor
        self.attractor = Attractor([Emitter(self.func, self.params_dict, self.start_pos, self.tail_end)], [], self.camera, self.settings)


# talk about using this parent class in design
class PopupWindow:
    def __init__(self, parent, on_close=None):
        self.parent = parent
        self.parent.resizable(False, False)
        self.frame = tk.Frame(self.parent)
        self.on_close = on_close

        self.exit_button = tk.Button(self.parent, text="Save and exit", command=self.exit_window)

    def exit_window(self, *args, **kwargs):
        if self.on_close is not None:
            self.on_close(*args, **kwargs) #talk about arg passing in design

        self.parent.destroy()


from tkinter import ttk


class RenderBar:
    def __init__(self, parent, attractor):
        self.parent = parent
        self.parent.resizable(False, False)
        self.frame = tk.Frame(self.parent)
        self.parent.geometry("200x50")
        self.attractor = attractor
        self.settings = self.attractor._settings

        self.progress_bar = ttk.Progressbar(self.parent, length=180, max=self.attractor._settings.iters)
        self.label = tk.Label(self.parent, text="Rendering...")

        self.progress_bar.place(x=10,y=10)
        self.label.place(x=10,y=25, width=180, height=20)

    def start(self):
        t = threading.Thread(target = self.attractor.render, args = (self.settings.resolution, self.settings.extension, self.progress_bar, self.destroy))
        t.start()

    def destroy(self):
        self.parent.destroy()


# Gist credit: https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01. Licensed under https://mozilla.org/MPL/2.0/.
from core.mp035_ScrollFrame import ScrollFrame


class ParameterSettingsWindow(PopupWindow):
    def __init__(self, parent, params, params_save_callback, existing_params={},default_value=0):
        super().__init__(parent, on_close=self.save)
        self.parent.geometry("400x200")
        self.params, self.params_save_callback = params, params_save_callback
        keys, vals = [], []
        for k,v in zip(existing_params.keys(), existing_params.values()):
            keys.append(k)
            if k in self.params:
                vals.append(v)
            else:
                vals.append(default_value)
        self.param_dict = dict(zip(keys, vals))

        self.param_scroll_frame = ScrollFrame(self.parent)
        self.entries_dict = None
        self.sliders_dict = None
        self.display()

        self.param_scroll_frame.place(x=12,y=5, height=135, width=375)
        self.exit_button.place(x=12, y=147, height=45, width=375)

        logging.debug("ParameterSettings window initialized.")

    def display(self):
        dict_keys = []
        param_slider_dict_vals = []
        param_entry_dict_vals = []

        for index, param in enumerate(self.params):
            dict_keys.append(param)

            tk.Label(self.param_scroll_frame.viewPort, text=param, width=6).grid(row=index,columnspan=2,column=0, padx=5, pady=5)

            new_slider = tk.Scale(self.param_scroll_frame.viewPort, orient=tk.HORIZONTAL, from_=-10, to=10, showvalue=False, width=10,length=240, command=self.sliders_updated)
            new_slider.grid(row=index, columnspan=20, column=2, pady=5)
            param_slider_dict_vals.append(new_slider)

            new_entry = tk.Entry(self.param_scroll_frame.viewPort, width=6)
            new_entry.grid(row=index, columnspan=2, column=23, padx=5, pady=5)
            param_entry_dict_vals.append(new_entry)

            new_slider.set(self.param_dict[param]*10)

        self.entries_dict = dict(zip(dict_keys, param_entry_dict_vals))
        self.sliders_dict = dict(zip(dict_keys, param_slider_dict_vals))

    def sliders_updated(self, *args):
        for param, slider, entry in list(zip(self.entries_dict.keys(), self.sliders_dict.values(),self.entries_dict.values())):
            val = slider.get()/10
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(val))

    def save(self):
        logging.debug("Closing ParameterSettings window...")
        keys, vals = [],[]
        self.params_dict = dict(list(zip(self.entries_dict.keys(),list(map(lambda x:float(x.get()), self.entries_dict.values())))))
        self.params_save_callback(self.params_dict)


class VWinConfigWindow(PopupWindow):
    def __init__(self, parent, save_callback):
        super().__init__(parent, on_close=self.save)
        self.parent.geometry('725x350')
        self.save_callback = save_callback

        self.search_canvas = tk.Canvas(self.parent)

        self.reset_button        = tk.Button(self.parent, text="Reset", command=self.reset)
        self.save_button         = tk.Button(self.parent, text="Save\nVWin", command=self.save_as_file)
        self.load_button         = tk.Button(self.parent, text="Load\nVWin", command=self.load_from_file)
        self.swap_sliders_button = tk.Button(self.parent, text="Swap\nXY", command=self.swap_sliders)
        self.swap_axis_button    = tk.Button(self.parent, text="Swap\nAxis", command=self.swap_axis)

        self.x_start_label   = tk.Label(self.parent, text="X Start")
        self.y_start_label   = tk.Label(self.parent, text="Y Start")
        self.x_end_label     = tk.Label(self.parent, text="X End")
        self.y_end_label     = tk.Label(self.parent, text="Y End")
        self.scale_label     = tk.Label(self.parent, text="Scale")
        self.x_axis_label    = tk.Label(self.parent, text="X Axis")
        self.y_axis_label    = tk.Label(self.parent, text="Y Axis")
        self.x_val_label     = tk.Label(self.parent, text="X: 0")
        self.y_val_label     = tk.Label(self.parent, text="Y: 0")

        self.x_start_slider = tk.Scale(self.parent, from_=-10, to=10,  orient=tk.VERTICAL,   command=self.sliders_updated)
        self.y_start_slider = tk.Scale(self.parent, from_=-10, to=10,  orient=tk.VERTICAL,   command=self.sliders_updated)
        self.x_end_slider   = tk.Scale(self.parent,   from_=-10, to=10,  orient=tk.VERTICAL,   command=self.sliders_updated)
        self.y_end_slider   = tk.Scale(self.parent,   from_=-10, to=10,  orient=tk.VERTICAL,   command=self.sliders_updated)
        self.scale_slider   = tk.Scale(self.parent,   from_=1,   to=100, orient=tk.VERTICAL,   command=self.scale_changed)

        self.axis_options = ["x", "y", "p1", "p2"]

        self.x_axis = tk.StringVar()
        self.x_axis.set("x")
        self.x_axis_dropdown = tk.OptionMenu(self.parent, self.x_axis, *self.axis_options)

        self.y_axis = tk.StringVar()
        self.y_axis.set("y")
        self.y_axis_dropdown = tk.OptionMenu(self.parent, self.y_axis, *self.axis_options)

        self.scale_entry    = tk.Entry(self.parent)
        self.x_start_entry  = tk.Entry(self.parent)
        self.y_start_entry  = tk.Entry(self.parent)
        self.x_end_entry    = tk.Entry(self.parent)
        self.y_end_entry    = tk.Entry(self.parent)

        self.search_canvas .place(x=9, y=15, width=320, height=200)

        self.x_start_label  .place(x=417-25, y=2,   width=40, height=15)
        self.y_start_label  .place(x=459-20, y=2,   width=40, height=15)
        self.x_end_label    .place(x=501-15, y=2,   width=40, height=15)
        self.y_end_label    .place(x=543-10, y=2,   width=40, height=15)
        self.scale_label    .place(x=369-30, y=2,   width=40, height=15)
        self.x_axis_label   .place(x=9,      y=228, width=45, height=15)
        self.y_axis_label   .place(x=9,      y=269, width=45, height=15)
        self.x_val_label    .place(x=287,    y=228, width=45, height=15)
        self.y_val_label    .place(x=287,    y=269, width=45, height=15)

        self.scale_slider  .place(x=369-30, y=15, width=40, height=275)
        self.x_start_slider.place(x=417-25, y=15, width=40, height=275)
        self.y_start_slider.place(x=459-20, y=15, width=40, height=275)
        self.x_end_slider  .place(x=501-15, y=15, width=40, height=275)
        self.y_end_slider  .place(x=543-10, y=15, width=40, height=275)

        self.x_axis_dropdown.place(x=65, y=224, width=214, height=25)
        self.y_axis_dropdown.place(x=65, y=265, width=214, height=25)

        self.scale_entry  .place(x=369-30, y=299, width=40, height=45)     # weird x values
        self.x_start_entry.place(x=417-25, y=299, width=40, height=45)     # weird x values
        self.y_start_entry.place(x=459-20, y=299, width=40, height=45)     # weird x values
        self.x_end_entry  .place(x=501-15, y=299, width=40, height=45)     # weird x values
        self.y_end_entry  .place(x=543-10, y=299, width=40, height=45)     # weird x values

        self.reset_button        .place(x=580, y=299, width=140, height=45)
        self.save_button         .place(x=580, y=15,  width=140, height=45)
        self.load_button         .place(x=580, y=75,  width=140, height=45)
        self.swap_sliders_button .place(x=580, y=135, width=140, height=45)
        self.swap_axis_button    .place(x=580, y=195, width=140, height=45)
        self.exit_button         .place(x=9,   y=299, width=320, height=45)

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

    def save_as_file(self):
        pass  # todo: .vwin files

    def load_from_file(self):
        pass

    def scale_changed(self, *args):
        pass

    def swap_axis(self):
        x = self.x_axis.get()
        y = self.y_axis.get()
      
        self.x_axis.set(y)
        self.y_axis.set(x)

    def swap_sliders(self):
        xs = float(self.x_start_slider.get())
        ys = float(self.y_start_slider.get())
        xe = float(self.x_end_slider.get())
        ye = float(self.y_end_slider.get())

        self.x_start_slider.set(ys)
        self.y_start_slider.set(xs)
        self.x_end_slider  .set(ye)
        self.y_end_slider  .set(xe)
    
    def save(self):
        # Needs to pass out all of this
        xs = float(self.x_start_entry.get())
        ys = float(self.y_start_entry.get())
        xe = float(self.x_end_entry.get())
        ye = float(self.y_end_entry.get())
        self.save_callback(xs, ys, xe, ye)

    def reset(self):
        self.x_start_slider.set(0)
        self.y_start_slider.set(0)
        self.x_end_slider.set(0)
        self.y_end_slider.set(0)
        self.sliders_updated()


class SettingsWindow(PopupWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.geometry('750x450')

        self.bar_callbacks = [self.general, self.rendering, self.files, self.color, self.ui, self.maths, self.update_method] #talk about the callbacks in development
        self.settings_bar = SettingsBar(parent, self.bar_callbacks)
        self.exit_button.place(x=25, y=395, width=700, height=45)

        self.actual_settings_frame = tk.Frame(self.parent)
        self.actual_settings_frame.place(x=122, y=12, width=616, height=370)

        logging.debug("Trying to render default (general) settings frame...") #talk about these algos in design
        self.frame_content = GeneralSettings
        self.frame_content(self.actual_settings_frame)

    @updates_settings_frame
    def general(self):
        logging.debug("User opened general tab of settings")
        self.frame_content = GeneralSettings

    @updates_settings_frame
    def rendering(self):
        logging.debug("User opened general tab of settings")
        self.frame_content = RenderingSettings

    @updates_settings_frame
    def files(self):
        logging.debug("User opened files tab of settings")
        self.frame_content = FilesSettings

    @updates_settings_frame
    def color(self):
        logging.debug("User opened color tab of settings")
        self.frame_content = ColorSettings

    @updates_settings_frame
    def ui(self):
        logging.debug("User opened ui tab of settings")
        self.frame_content = UISettings

    @updates_settings_frame
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

        self.general_button = tk.Button(self.parent, command=self.callbacks[0], text="Genera")
        self.rendering_button = tk.Button(self.parent, command=self.callbacks[1], text="Rendering")
        self.files_button = tk.Button(self.parent, command=self.callbacks[2], text="Files")
        self.color_button = tk.Button(self.parent, command=self.callbacks[3], text="Color")
        self.ui_button = tk.Button(self.parent, command=self.callbacks[4], text="UI")
        self.maths_button = tk.Button(self.parent, command=self.callbacks[5], text="Maths")
        self.update_button = tk.Button(self.parent, command=self.callbacks[6], text="Update")
        self.placeholder = tk.Label(self.parent)

        self.general_button.place(x=13, y=12, width=95, height=15)
        self.rendering_button.place(x=13, y=27, width=95, height=15)
        self.files_button.place(x=13, y=42, width=95, height=15)
        self.color_button.place(x=13, y=57, width=95, height=15)
        self.ui_button.place(x=13, y=73, width=95, height=15)
        self.maths_button.place(x=13, y=88, width=95, height=15)
        self.update_button.place(x=13, y=103, width=95, height=15)
        self.placeholder.place(x=13, y=118, width=95, height=265)


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
        self.insert_button     = tk.Button(self.parent, text="Insert new\ncolor",             command=self.insert)
        self.delete_button     = tk.Button(self.parent, text="Delete color\nat position",     command=self.delete)
        self.jump_next_button  = tk.Button(self.parent, text="Jump to\nnext color",           command=self.jump_next)
        self.reverse_button    = tk.Button(self.parent, text="Reverse\nColormap",             command=self.reverse)
        self.invert_button     = tk.Button(self.parent, text="Invert\nColors",                command=self.invert)
        self.jump_prev_button  = tk.Button(self.parent, text="Jump to\nprevious color",       command=self.jump_prev)
        self.adjoin_button     = tk.Button(self.parent, text="Adjoin Colormap\nfrom file",    command=self.adjoin)
        self.double_button     = tk.Button(self.parent, text="Compress and\ndouble colormap", command=self.double)
        self.jump_first_button = tk.Button(self.parent, text="Jump to\nfirst color",          command=self.jump_first)
        self.save_button       = tk.Button(self.parent, text="Save\nColormap",                command=self.save)
        self.load_button       = tk.Button(self.parent, text="Load New\nColormap",            command=self.load)
        self.jump_last_button  = tk.Button(self.parent, text="Jump to\nlast color",           command=self.jump_last)

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

    @updates_colormap_preview
    def insert(self):  # required new method
        output = cc.askcolor()[0]
        color = Color(*output, 255)
        self.colormap.insert_value(color, int(self.position_slider.get()))

    @updates_colormap_preview
    def delete(self):
        currentpos = self.position_slider.get()
        poslist = list(map(lambda x: x[1], self.colormap.get_gradient().__getattribute__("_color_peaks")))
        if currentpos in poslist:
            x = self.colormap.__getattribute__("_gradient").__getattribute__("_color_peaks")
            x.pop(poslist.index(currentpos))
            self.colormap = Colormap(Gradient(x))

    @updates_colormap_preview
    def jump_next(self):
        currentpos = self.position_slider.get()
        poslist = list(map(lambda x:x[1], self.colormap.get_gradient().__getattribute__("_color_peaks")))
        for index, val in enumerate(poslist):
            if val > currentpos:
                self.position_slider.set(poslist[index])
                return

    @updates_colormap_preview
    def invert(self):  # need a new method
        self.colormap.invert()

    @updates_colormap_preview
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

    @updates_colormap_preview
    def adjoin(self):
        logging.debug("User pressed button - 'Load Colormap'")
        filename = fd.askopenfilename(filetypes=[("Colormap File", "*.colormap"), ("Raw Text Colormap", "*.txt")], defaultextension=".cmp")
        logging.debug(f"Absolute filepath opened is {filename}")
        other_cmp = Colormap(None)  # None initialization is fine here as colormap is loaded
        other_cmp.load(filename)
        self.colormap += other_cmp
        self.colormap *= 100/len(self.colormap)

    @updates_colormap_preview
    def double(self):  # warraneted loads of common updates, added __stuff__ and had to change add logic to add the +1
        self.colormap = self.colormap + self.colormap
        self.colormap = self.colormap*0.5

    @updates_colormap_preview
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

    @updates_colormap_preview
    def jump_last(self):
        self.position_slider.set(self.colormap.get_gradient().__getattribute__("_color_peaks")[-1][1])

    @updates_colormap_preview
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

        self.algo_label     = tk.Label(self.parent, text="Sampling\nAlgorithm")
        self.x_res_label    = tk.Label(self.parent, text="X\nRes")
        self.y_res_label    = tk.Label(self.parent, text="Y\nRes")

        self.x_res_slider   = tk.Scale(self.parent, orient=tk.HORIZONTAL, from_=128, to=4096)
        self.y_res_slider   = tk.Scale(self.parent, orient=tk.HORIZONTAL, from_=128, to=4096)
        self.x_res_slider.set(1920)
        self.y_res_slider.set(1080)

        algo_options = ["Poisson-disc", "Quincux", "Grid", "Rotated Grid"]
        self.algo = tk.StringVar()
        self.algo.set("Poisson-disc")
        self.algo_dropdown = tk.OptionMenu(self.parent, self.algo, *algo_options)

        self.enable_button  = tk.Button(self.parent, text="Enable Supersampling", command=self.enable)
        self.reset_button   = tk.Button(self.parent, text="Reset to default", command=self.reset)

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
