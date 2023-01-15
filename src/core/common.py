import os
from math import floor, cos, sin
from typing import Callable, Union
from os import listdir, makedirs, getcwd, remove
from os.path import isfile, join, exists
import logging
from sys import exit
from datetime import datetime

# pylint: disable=logging-fstring-interpolation
# pylint: disable=invalid-name

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

def parse_eq(text: str) -> Callable: #this block hasnt been tested at all yet 09:51 12/01/23
    """
    Converts a stringed expression to a callable. params just start with %
    """
    error_y, error_x = False, False
    logging.debug("Parsing new equation...")
    if "x=" in text:
        start_x = text.find("x=")
        end_x = text.find("\\x")
        expression_x = text[start_x:end_x]
        loc={"x":1,"y":1,"t":2}
        logging.debug(f"X Expression was found - [{expression_x}]")
        try:
            exec("from math import *;"+expression_x,{},loc)  #pylint: disable = exec-used
            logging.debug("Expression appears to be error-free.")
        except Exception as e:
            logging.warning("Given expression errors, setting error flag to HIGH and falling back to defaults/default_eq_x.txt")
            logging.debug(f"Internal error - {e}")
            error_x = True
    if "x=" not in text or error_x:
        if "x=" not in text:
            logging.warning("No X equation found - defaulting to defaults/default_eq_x.txt")
        logging.info("Attempting to load from default file...")
        try:
            default = open("defaults/default_eq_x.txt","r",encoding="utf-8")
            expression_x = default.readlines[0]
            logging.info(f"Loading from default was successful. Loaded string is [{expression_x}]")
        except Exception as e:
            logging.error("Unable to load default equation - hardcoded fallback [x=xt] now in place.")
            logging.error(f"Internal error - {e}")
            expression_x = "x=x*t"
    
    if "y=" in text:
        start_y = text.find("y=")
        end_y = text.find("\\y")
        expression_y = text[start_y:end_y]
        loc={"x":1,"y":1,"t":2}
        logging.debug(f"Y Expression was found - [{expression_y}]")
        try:
            exec("from math import *;"+expression_y,{},loc)  #pylint: disable=exec-used
            logging.debug("Expression appears to be error-free.")
        except Exception as e:
            logging.warning("Given expression errors, setting error flag to HIGH and falling back to defaults/default_eq_y.txt")
            logging.debug(f"Internal error - {e}")
            error_y = True

    if "y=" not in text or error_y:
        if "y=" not in text:
            logging.warning("No Y equation found - defaulting to defaults/default_eq_y.txt")
        logging.info("Attempting to load from default file...")
        try:
            default = open("defaults/default_eq_y.txt","r",encoding="utf-8")
            expression_y = default.readlines[0]
            logging.info(f"Loading from default was successful. Loaded string is [{expression_y}]")
        except Exception as e:
            logging.error("Unable to load default equation - hardcoded fallback [y=yt] now in place.")
            logging.error(f"Internal error - {e}")
            expression_y = "y=y*t"
    
    def x_func(x, y, t):
        loc={"x":x,"y":y,"t":t}
        try:
            exec("from math import *;"+expression_x, {}, loc)  #pylint: disable=exec-used
        except Exception as e:
            logging.error(f"X function raised an error - {e} ")
            logging.critical("Program unsure how to continue. Exiting with code 1...")
            exit(1)
        return loc["x"]

    def y_func(x, y, t):
        loc={"x":x,"y":y,"t":t}
        try:
            exec("from math import *;"+expression_y, {}, loc)  #pylint: disable=exec-used
        except Exception as e:
            logging.error(f"X function raised an error - {e} ")
            logging.critical("Program unsure how to continue. Exting with code 1...")
            exit(1)
        return loc["y"]

    tuple_func = lambda a, t: (x_func(a[0], a[1], t), y_func(a[0], a[1], t))

    return tuple_func


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

    def hex(self):
        pass
        #todo: return hex value
    

class Gradient:
    """
    Class that manages color gradients.
    """
    def __init__(self, gradient: list[list[Color, int]]):
        self._color_peaks = sorted(gradient, key=lambda x: x[1])
        if len(gradient) <= 1: #1 or 0
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

    def left_padd(self, padding: int):
        """
        Shifts a gradient wholly left by in timespace an integer
        """
        return Gradient(list(map(lambda x: [x[0], x[1]+padding], self._color_peaks[:])))

    def __add__(self, other):
        if not isinstance(other, Gradient):
            raise TypeError

        right_color_peaks = list(map(lambda x: [x[0], x[1]+len(self)], other._color_peaks))
        return Gradient(self._color_peaks + right_color_peaks)

    def __mul__(self, scalar: int):
        return Gradient(list(map(lambda x: [x[0], x[1]*scalar], self._color_peaks[:])))

    def __rmul__(self, scalar: int):
        return self*scalar


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


class Image:
    """
    Class for an output image
    """
    def __init__(self, pixels: list[list[Point]], extension: str) -> None:                       #Extension object?
        self.pixels, self.extension = pixels, extension

    def write(self, path: str) -> bool:
        """
        Writes the image to a path
        """
        logging.critical("Not yet implemented method write of Image.")
        return "not implemented", path


class Camera:
    """
    Class that manages camera transforms
    """
    def __init__(self, xpos:float, ypos:float , rotation:float, aspect_ratio:tuple[int,int], scale:float):
        self._pos   = (xpos, ypos)
        self._rot   = rotation
        self._scale = scale
        self._ar    = aspect_ratio
        self.implicit_res = [x*scale for x in aspect_ratio]

        self._translate = lambda x,y: (x-self._pos[0], y-self._pos[1])
        self._rotate    = lambda x,y: (x*cos(self._rot)-y*sin(self._rot), x*sin(self._rot)+y*cos(self._rot))
        self._scale     = lambda x,y: 1 if all([abs(self._translate(x,y)[0])<self._ar[0]*self._scale,abs(self._translate(x,y)[1])<self._ar[1]*self._scale]) else 0

        logging.debug(f"New Camera object instantiated at {hex(id(self))}")

    def transform_point(self, x_val: float, y_val:float) -> Union[tuple, None]: #relative to the centered camera plane
        """
        Transforms a point to be in space relative to a camera plane with centered origin
        """
        if self._scale(x_val,y_val):
            x_val,y_val = self._translate(x_val,y_val)
            return self._rotate(x_val,y_val)
        else:
            return None

    def transform_space(self, points: list[list[float]]) -> Union[list[list[float]], list]:
        """
        Transform a set of points
        """
        return list(filter(lambda x:x is not None, map(lambda vec: self.transform_point(vec[0], vec[1]), points)))


class Emitter:
    """
    Where the magic happens
    """
    def __init__(self, x_func: Callable[[int], int], y_func: Callable[[int], int], pos: list[int, int], tail_end: int = 1000, time_offset: int=0) -> None:
        self._x_func, self._y_func, self._pos, self._tail_end = x_func, y_func, pos, tail_end
        self._time = time_offset

        logging.debug(f"New Emitter object instantiated at {hex(id(self))}")
    def new_point(self) -> tuple[list, int, bool]:
        """
        Generate a new point
        """
        self._pos = (lambda f_x, f_y, x,y: [f_x(x), f_y(y)])(self._x_func, self._y_func, self._pos[0], self._pos[1]) #shut the fuck up linter iifes are cool
        self._time += 1
        return self._pos[:], self._time, (self._time -1 > self._tail_end)


class Settings:
    """
    Will hold preferences. Just a datastruct.
    """


class Attractor:
    """
    Class that defines an attractor and therefore the output image
    """
    def __init__(self, emitters: list[Emitter], points: list, camera: Camera,settings: Settings) -> None:
        self._emitters = emitters
        self._points   = points
        self._settings = settings
        self._size     = len(self._points)
        self._camera   = camera

        logging.debug(f"New Attractor object instantiated at {hex(id(self))}")

    def timestep(self) -> None:
        """
        Advance time.
        """
        for emitter in self._emitters:
            colormap = self._settings.colormap
            (new_x, new_y), time, displayed = emitter.new_point(self)
            if displayed:
                self._points.append(Point(colormap.get_value(time), [new_x, new_y]))

    def render(self, resolution: list[int], extension: str) -> Image:
        """
        Render self.
        """
        _ = resolution, extension
        return self._camera.transform_space(self._points) #todo: this
    
    