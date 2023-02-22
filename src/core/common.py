import os
import threading
from math import floor, cos, sin, ceil
from threading import Thread, Event
from typing import Callable, Union
from os import listdir, makedirs, getcwd, remove
from os.path import isfile, join, exists
import logging
from sys import exit
from datetime import datetime

# pylint: disable=logging-fstring-interpolation
# pylint: disable=invalid-name


def dict_join(x: dict, y: dict) -> dict:
    """
    Joins two dicts
    """
    return dict(zip(list(x.keys())+list(y.keys()), list(x.values())+list(y.values()))) #  i wrote this with a migraine


def get_params(rawtext):
    """
    Returns a dict_keys object containing  parameter names as strings
    """
    loc = {"x":1,"y":1,"t":0,"dx":None,"dy":None}
    glo = {}
    exec("from math import*", glo, loc)
    params = {}

    for line in filter(lambda x:x!="", rawtext.split("\n")):
        def process_line(loc, params):
            x=dict_join(params, loc)
            try:
                exec(line, glo, x)
            except NameError as e:
                new_param = str(e).split("'")[1]
                params = dict_join(params, {new_param: 1})
                return process_line(x, params)
            except Exception as e:
                logging.error(f"Internal Error - {e}")
            return x, params
        loc, params = process_line(loc, params)
    return params.keys()


def initialise_logger(debug: bool):
    """
    Initialises the logger
    """
    initialisation_time = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")

    logdir = f"{getcwd()}/core/logs"
    logs = map(lambda x:x.replace(".log", ""), os.listdir(logdir))

    debug_logs = filter(lambda x:x[0:9]=="DEBUG_LOG", logs)
    logs = filter(lambda x:x[0:3]=="LOG", logs)
    debug_logs = list(map(lambda x:x.replace("DEBUG_LOG-",""), debug_logs))
    logs = list(map(lambda x: x.replace("LOG-", ""), logs))

    debug_logs.sort(key=lambda date: datetime.strptime(date, "%m-%d-%Y_%H-%M-%S"))
    logs.sort(key=lambda date: datetime.strptime(date, "%m-%d-%Y_%H-%M-%S"))

    while len(logs) >= 3:
        os.remove(f"{logdir}/LOG-{logs[0]}.log")
        logs.pop(0)

    while len(debug_logs) >= 3:
        os.remove(f"{logdir}/DEBUG_LOG-{debug_logs[0]}.log")
        debug_logs.pop(0)

    if debug:
        logging.basicConfig(filename = f"{logdir}/DEBUG_LOG-{initialisation_time}.log", level=logging.DEBUG)
    else:
        logging.basicConfig(filename=f"{logdir}/LOG-{initialisation_time}.log", level=logging.WARNING)

    logging.info(f'Logging started @ {datetime.now().strftime("%H:%M:%S")}')


def structure_check(dir: str):
    """
    Runs a check on the given directory to make sure it has an operational structure, and tries to regenerate the correct
    structure.

    Note this does NOT check for a core directory or a main.py file. This is because if this is running said directories
    should already exist.

    Could raise logging issues.
    """
    if not exists(dir + "/cache"):
        logging.warning("No cache directory found, possibly deleted by user. Regenerating...")
        try:
            makedirs(dir + "/cache")
            file = open(dir + "/cache/.gitignore","w+", encoding="utf-8")
            file.write("""*\n!.gitignore""")
            file.close()
            logging.info("Regeneration of cache files successful.")
        except Exception as e:
            logging.critical("Regeneration of cache directory failed. Program is unable to cache files - exiting.")
            logging.error(f"Internal error - {e}")
            exit(126)

            # Exit code 126 - Cannot execute.
            # Attempting to run the mainthread past a structure check point would raise a DirectoryNotFound error
            # So it's more practical to log a message that makes sense and just exit with an error code.

    if not exists(dir + "/user_files"):
        logging.warning("No user_files directory found, possibly deleted by user. Regenerating...")
        try:
            makedirs(dir + "/cache")
            f = open(dir + "/cache/.gitignore","w+",encoding="utf-8")
            f.write("""*\n!.gitignore""")
            f.close()
            logging.info("Regeneration of user_files successful.")
        except Exception as e:
            logging.error("Regeneration failed:")
            logging.error(f"Internal error - {e}")

            # Program works fine without this user_files directory access, however this could cause issues in saving
            # or loading.
    if not exists(dir + "/defaults"):
        logging.warning("No defaults directory found, possibly deleted by user. Regenerating...")
        try:
            makedirs(dir + "/defaults")
            logging.info("Regeneration of directory successful.")
            logging.critical("Default files are missing - directory was regenerated but no way to curl the files has been implemented.")  # todo: defaults regenerated

            remove(dir+"/defaults")
            logging.info("Defaults directory removed to avoid confusion. Exiting...")
            exit(126)

        except Exception as e:
            logging.error("Regeneration failed:")
            logging.error(f"Internal error - {e}")

    if not exists(dir + "/samples"):

        # No point regenerating this as it'd have to be cloned from the repo and that requires git to be installed.
        # Could do a check for git on PATH then use a dialogue box?
        # Kinda pointless though, samples are bundled into the repository anyway so the user has either deleted them
        # or the installation hasn't gone well

        logging.warning("No samples found, possibly deleted by user.")

    logging.info("StructureCheck Complete.")


def parse_eq(rawtext):
    params = get_params(rawtext)

    os.remove(os.path.normpath(os.getcwd() + os.sep + os.pardir) + "/src/cache/user_func.py")
    f = open(os.path.normpath(os.getcwd() + os.sep + os.pardir) + "/src/cache/user_func.py", "w+")
    f.write("from math import*\n")
    kwargs = ",".join([x + "=0" for x in list(params)])
    f.write(f"def user_defined_func(x,y,t{',' + kwargs if len(kwargs) > 0 else ''}):\n")
    indent = rawtext.split("\n")
    for each in indent:
        f.write("    " + each + "\n")
    f.write("    return dx,dy")
    f.close()
    try:
        import sys
        sys.path.append(os.path.normpath(os.getcwd() + os.sep + os.pardir) + "/src/cache/")
        import user_func

    except Exception as e:
        logging.critical(e)
        exit()

    return params, user_func.user_defined_func


def _edit(inner: Callable) -> Callable:
    """
    Decorator for Point that manages the amount of times it has been edited
    """
    def outer(*args) -> Callable:
        args[0]._edits+=1
        return inner(*args)
    return outer


def chebyshev_dist(vec1: list[float, float], vec2: list[float, float]) -> float: # unused?
    """
    Finds the chebyshev distance between two points.
    """
    (x_1, y_1), (x_2, y_2) = vec1, vec2
    return max(abs(x_1-x_2), abs(y_1-y_2))


class WorkerThread(threading.Thread):
    """
    Thread with a stop method
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop = Event()

    def stop(self) -> None:
        self._stop.set()

    def is_stopped(self) -> bool:
        return self._stop.is_set()


class RangeError(ValueError):
    """ Honestly not sure why this is required. """
    def __init__(self):
        logging.critical("Internal Error - RangeError")


class Color:
    """
    Class that manages RGBA values, and blending of colors
    """
    def __init__(self, red: int, green: int, blue: int, alpha: int):
        self.alpha, self.red, self.blue, self.green = alpha, red, blue, green

    def __add__(self, other):
        new_alpha = self.alpha/255 + other.alpha/255*(1-self.alpha/255)
        result = Color(min(floor((self.red/255   * self.alpha/255 + other.red/255   * other.alpha/255) * 255), 255),
                       min(floor((self.green/255 * self.alpha/255 + other.green/255 * other.alpha/255) * 255), 255),
                       min(floor((self.blue/255  * self.alpha/255 + other.blue/255  * other.alpha/255) * 255), 255),
                       floor(new_alpha * 255))
        return result

    def hex(self) -> str:
        return f"#{('0x%02X' % self.red)[2:]}{('0x%02X' % self.green)[2:]}{('0x%02X' % self.blue)[2:]}".lower()

    def invert(self) -> None:
        self.red = 255 - self.red
        self.blue = 255 - self.blue
        self.green = 255 - self.green


class Gradient:
    """
    Class that manages color gradients.
    """
    def __init__(self, gradient: list[list[Color, int]]):
        self._color_peaks = sorted(gradient, key=lambda x: x[1])
        if len(gradient) <= 1: # 1 or 0
            self._range = len(gradient)
        else:
            self._range = abs(self._color_peaks[0][1] - self._color_peaks[-1][1])

    def __len__(self) -> int:
        return self._range

    def __getitem__(self, val: int):
        rel_pos = None
        val = val - val//len(self)
        for index, (color, position) in enumerate(self._color_peaks):
            if position == val:
                return color
            if position > val:
                next_color,prev_color = color,self._color_peaks[index-1][0]
                rel_pos = val-self._color_peaks[index-1][1]
                range_between = position - self._color_peaks[index-1][1]
                break
        if rel_pos is None:
            logging.error("Gradient object received invalid index.")
            raise RangeError
        red   = floor(prev_color.red   +(next_color.red   - prev_color.red)   * (rel_pos/range_between))
        green = floor(prev_color.green +(next_color.green - prev_color.green) * (rel_pos/range_between))
        blue  = floor(prev_color.blue  +(next_color.blue  - prev_color.blue)  * (rel_pos/range_between))
        alpha = floor(prev_color.alpha +(next_color.alpha - prev_color.alpha) * (rel_pos/range_between))

        return Color(red, green, blue, alpha)

    def __add__(self, other):
        if not isinstance(other, Gradient):
            raise TypeError

        right_color_peaks = [[x[0], x[1]+len(self)] for v, x in enumerate(other._color_peaks)]
        right_color_peaks[0][1]+=1
        return Gradient(self._color_peaks + right_color_peaks)

    def __mul__(self, scalar: Union[float, int]):
        return Gradient(list(map(lambda x: [x[0], ceil(x[1]*scalar)], self._color_peaks[:])))

    def __rmul__(self, scalar: Union[float, int]):
        return self*scalar

    def left_padd(self, padding: int):
        """
        Shifts a gradient wholly left by in timespace an integer
        """
        return Gradient(list(map(lambda x: [x[0], x[1]+padding], self._color_peaks[:])))

    def invert(self) -> None:
        """
        Inverts all colors in a gradient
        """
        for color, peak in self._color_peaks:
            color.invert()


class Colormap:
    """
    Encapsulates gradient, and saves and loads
    """
    def __init__(self, gradient: Gradient):
        self._gradient = gradient

    def set_gradient(self, grad: Gradient):
        """
        Setter for gradient
        """
        self._gradient = grad

    def get_gradient(self) -> Gradient:
        """
        Getter for gradient
        """
        return self._gradient

    def get_value(self, time: int) -> Color:
        """
        Returns the color at a time
        """
        return self._gradient[time]

    def __len__(self):
        return len(self._gradient)

    def __add__(self, other):
        return Colormap(self.get_gradient() + other.get_gradient())

    def __mul__(self, other):
        return Colormap(self.get_gradient() * other)

    def __rmul__(self, other):
        return Colormap(self.get_gradient() * other)

    def __reversed__(self):
        x = self.get_gradient().__getattribute__("_color_peaks")
        cols = list(map(lambda a:a[0], x))
        positions = list(map(lambda a: a[1], x))
        new = list(zip(cols[::-1], positions))
        self.get_gradient().__setattr__("_color_peaks", new)
        return self

    def invert(self) -> None:
        """
        Inverts all colors in a colormap
        """
        self._gradient.invert()

    def left_padd(self, amount) -> None:
        """
        Encapsulates the inner gradients' left padd
        """
        self.set_gradient(self.get_gradient().left_padd(amount))

    def insert_value(self, color: Color, time: int) -> None: #todo: move this to the Gradient class and encapsulate
        """
        Inserts a new color into the color peaks.
        """
        to_insert = [color, time]
        logging.warning("Protected access of _color_peaks in method insert_value - could maybe cause issues?")
        x = [a[:] for a in self.get_gradient()._color_peaks[:]]
        for index, (color, value) in enumerate(x):
            if time == value:
                x[index] = to_insert
                self._gradient.__setattr__("_color_peaks", x)
                return
        for index, (color, value) in enumerate(x): # talk about the bs where this would try and insert 100, 0, 100
            if time < value:
                x.insert(index, to_insert)
                self._gradient.__setattr__("_color_peaks", x)
                return

        x.append(to_insert)
        self._gradient.__setattr__("_color_peaks", x)

    def save(self, path: str):
        """
        Saves the colormap object into path.colormap
        """
        logging.debug(f"Saving colormap to {path}.colormap")
        data = self._gradient._color_peaks[:] #protected access is fine as it is a copy
        if path[-1] != "/":
            try:
                file = open(path+".colormap", "w+", encoding="utf-8")
                logging.debug(f"Successfully opened {path}.colormap")
            except Exception as e:
                logging.error("Saving colormap failed")
                logging.error(f"Internal error - {e}")
        else:
            logging.info("Filename was not specified, only directory. Creating a new unnamed colormap file...")
            try:
                files_in_dir = [file for file in listdir(path) if isfile(join(path, file))]                   #list files in dir
                filtered_files = list(filter(lambda x:"unnamed_colormap" in x, files_in_dir))                 #filter unnamed_colormap-like files
                file = open(path+f'/unnamed_colormap_{len(filtered_files)}.colormap',"w+",encoding="utf-8")       #create a new colormap without overwriting existing ones (hopefully)
                logging.debug(f"Successfully opened {path}/unnamed_colormap_{len(filtered_files)}.colormap")
            except Exception as e:
                logging.error("Saving colormap failed")
                logging.error(f"Internal error - {e}")
        for color, pos in data:
            logging.debug("Attempting to write colormap data to file...")
            try:
                file.write(f'{color.red}, {color.green}, {color.blue}, {color.alpha} @ {pos}')
                file.write("\n")
                logging.debug("Writing to file was a success.")
            except:
                logging.error("Writing failed.")
                logging.error(f"Internal error - {e}")
        file.close()

    def load(self, path: str) -> bool:
        """
        Load a colormap file. Returns True if successful, False otherwise.
        """
        logging.debug(f"Loading colormap from {path}")

        file = open(path, "r", encoding="utf-8")
        new_gradient = []
        try:
            for line in file.readlines():
                line = line.split(" @ ")
                (red, green, blue, alpha), pos = (tuple(map(int, line[0].split(", "))), int(line[1]))
                new_gradient.append([Color(red, green, blue, alpha), pos])
            self.set_gradient(Gradient(new_gradient))
            file.close()
            logging.debug("Loading success.")
            logging.debug(f"Loaded new Gradient object at {hex(id(self.get_gradient()))} with parent at {hex(id(self))}")
            return True
        except Exception as e:
            logging.error("Loading failed.")
            logging.error(f"Internal error - {e}")
            file.close()
            return False


class Point:
    """
    Class manages a point position and color.
    """
    def __init__(self, color: Color, pos: list):
        self._color = color
        self._pos = pos
        self._edits = 0

    @_edit
    def set_color(self, col: Color) -> None:
        """
        Setter for color value
        """
        self._color = col

    @_edit
    def blend_color(self, col: Color) -> None:
        """
        Blends the points color with another color
        """
        self._color += col

    def get_color(self) -> Color:
        """
        Getter for color value
        """
        return self._color

    def get_pos(self) -> list:
        """
        Getter for pos value
        """
        return self._pos[:]

    def rotate(self, angle, origin):
        """
        Rotates the point around an origin
        """
        px, py = self.get_pos()
        ox, oy = origin
        sinA = sin(angle)
        cosA = cos(angle)
        nx = ox + cosA*(px-ox)-sinA*(py-oy)
        ny = oy + sinA*(px-ox)-cosA*(py-oy)
        self._pos = [nx,ny]

    def translate(self, vector: list[float]):
        """
        Translates a point by a vector
        """
        vx,vy = vector
        px,py = self._pos
        self._pos = [px+vx, py+vy]

    def scale_by_dims(self, scalars: list[float]):
        self._pos = [[x*y for x, y in zip(self.get_pos(), scalars)]]


class Camera:
    """
    Class that manages camera transforms
    """
    def __init__(self, top_left: list[float, float], bottom_right: list[float, float], rotation: float):
        self._plane = [top_left, bottom_right]
        self._center = [(top_left[0] + bottom_right[0])/ 2, (top_left[1] + bottom_right[1])/ 2]
        self._rotation = rotation

        logging.debug(f"New Camera object instantiated at {hex(id(self))}")

    def get_plane(self, space: list[Point]) -> list[Point]:
        """
        Returns the perspective plane of the camera on a spcae
        """
        (min_x, max_y),(max_x, min_y) = self._plane
        plane = []
        for point in space:
            x,y = point.get_pos()
            if min_x <= x <= max_x and min_y <= y <= max_x:
                if self._rotation != 0.0:
                    point.rotate(-self._rotation, self._center)
                plane.append(point)
        return plane

    def scale_to_resolution(self, plane: list[Point], res: list[int]):
        """
        Scales the perspective plane to span a resolution
        """
        (min_x, max_y), (max_x, min_y) = self._plane
        translate = [-min_x, -min_y]  # translates the top left point in the plane to the 0,0 pixel position
        # lc's are faster :)
        [x.translate(translate) for x in plane]
        [x.scale_by_dims([res[0]/(max_x-min_y), res[1]/(max_y-min_y)]) for x in plane]  # scales it to the resolution

        return plane


class Emitter:
    """
    Where the magic happens
    """
    def __init__(self, func: Callable, params: dict, pos: list[int, int], tail_end: int = 1000, time_offset: int=0) -> None:
        self._func, self._pos, self._tail_end = func, pos, tail_end
        self._params = params
        self._time = time_offset

        logging.debug(f"New Emitter object instantiated at {hex(id(self))}")

    def new_point(self) -> tuple[list, int, bool]:
        """
        Generate a new point
        """
        x, y = list(self._pos)
        t = self._time
        self._pos = self._func(x, y, t, **self._params)
        self._time += 1
        return self._pos[:], self._time, (self._time >= self._tail_end)


class Settings:
    """
    Will hold preferences. Just a datastruct.
    """
    def __init__(self, colormap, colormap_scale_factor = 100):
        self.colormap = colormap
        self.colormap_scale_factor = colormap_scale_factor
        self.resolution = [4096, 4096]  # hardcoded defaults
        self.extension = "PNG"
        self.save_directory = getcwd() + "/user_files/"
        self.iters = 1_000_000
        self.blend_mode = "add"


from tkinter import Canvas, END
from PIL import Image
from itertools import groupby


class Attractor:
    """
    Class that defines an attractor and therefore the output image
    """
    def __init__(self, emitters: list[Emitter], points: list, camera: Camera, settings: Settings, supersampled=False, supersampling_factor=None) -> None:
        self.supersampled = supersampled
        self.supersampling_factor = supersampling_factor
        self._emitters = emitters
        self._points   = points
        self._settings = settings
        self._size     = len(self._points)
        self._camera   = camera
        self.colormap = self._settings.colormap * self._settings.colormap_scale_factor
        self.colormap_len = len(self.colormap)

        logging.debug(f"New Attractor object instantiated at {hex(id(self))}")

    def timestep(self) -> list:
        """
        Advance time.
        """
        newpoints = []
        for emitter in self._emitters:
            pos, time, displayed = emitter.new_point()
            if displayed:
                newpoints.append(Point(self.colormap.get_value(time % self.colormap_len), pos))
        self._points += newpoints

        return self._camera.get_plane(newpoints)

    def async_render(self, resolution: list[int], canvas: Canvas):
        canvas.delete("all")

        class RenderThread(WorkerThread):  # This is so weird
            def __init__(self, timestep, colormap, camera, canvas_inner, resolution_inner):
                super().__init__()
                self.timestep = timestep
                self.colormap = colormap
                self.camera = camera
                self.canvas = canvas_inner
                self.resolution = resolution_inner
                self.iters = 0

            def run(self) -> None:
                renderer = Renderer(self.resolution, self.timestep, self.canvas, self.colormap, self.camera)
                while not self.is_stopped() and self.iters < 25000:
                    next(renderer)
                    self.iters += 1

        thread = RenderThread(self.timestep, self.colormap, self._camera, canvas, resolution)
        return thread

    def render(self, resolution: list[int], extension: str, progress_bar, destroy) -> Image:
        """
        Render self.
        """
        renderer = Renderer(resolution, self.timestep, None, self.colormap, self._camera)
        points = []
        x = self._settings.iters
        for i in range(x-1):
            if i % 100 == 0:
                progress_bar.step(100)
            points.append(next(renderer))

        img = Image.new('RGBA', (resolution[0], resolution[1]), color=(0,0,0,255))
        points = list(filter(lambda x: x is not None, points))
        if self._settings.blend_mode == "add":
            newpoints = []
            for coord, colors in groupby(points, lambda x: [x[0],x[1]]):
                colors = [x[2] for x in list(colors)]
                newpoints.append([coord[0], coord[1], sum(colors[1:], start=colors[0])])  # NOTE: sum(B) is actually 0+B[0]+B[1] ... B[len(B)]. That's so stupid. - Ace
            points = newpoints
        for point in points:
            x, y, c = point
            img.putpixel((x, y), (c.red, c.green, c.blue, c.alpha))
        img.save(self._settings.save_directory+"image_test."+self._settings.extension.lower())

        destroy()
        return img


class Renderer:
    def __init__(self, resolution: list[int], timestep_callback, canvas, colormap: Colormap, camera: Camera) -> None:
        self.colormap = colormap
        self.resolution = resolution
        self.canvas = canvas
        self.timestep = timestep_callback
        self.camera = camera
        self.time = 0
        if self.canvas is None:
            self.inner = self.next_inner_img
        else:
            self.inner = self.next_inner_canvas

    def __next__(self):
        return self.inner()

    def next_inner_img(self):
        self.time += 1
        for point in self.camera.scale_to_resolution(self.timestep(), self.resolution):
            x, y = point.get_pos()
            return floor(x), floor(y), point.get_color()

    def next_inner_canvas(self):
        self.time += 1
        if self.time > len(self.colormap):
            self.time = 0
        for point in self.camera.scale_to_resolution(self.timestep(), self.resolution):
            x, y = point.get_pos()
            hex_color = point.get_color().hex()
            self.canvas.create_line(x, y, x + 1, y, fill=hex_color)

def display_colormap_on_canvas(canvas: Canvas, colormap: Colormap, width, height) -> None:
    colormap_len = len(colormap)

    stretch_factor = height/colormap_len  # generally should be > 1 and integer but could cause issues
    for i in range(colormap_len+1):
        canvas.create_rectangle(0, i*stretch_factor, width, height, fill=colormap.get_value(i).hex(), outline="")


class TextChangeListener(WorkerThread):
    def __init__(self, text_box, callback):
        super().__init__()
        self.text_box, self.callback = text_box, callback
        self.last_get = self.text_box.get(1.0, END)

    def run(self) -> None:
        while not self.is_stopped():
            next_get = self.text_box.get(1.0, END)
            if self.last_get != next_get:
                self.callback()
            self.last_get = next_get
