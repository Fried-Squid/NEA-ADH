from math import floor, cos, sin
from typing import Callable, Union, List
from os import listdir, makedirs
from os.path import isfile, join, exists
import logging
from sys import exit
from datetime import datetime

def initialise_logger(debug):
    """
    Initialises the logger
    """
    initialisation_time = datetime.now().strftime("%m/%d/%Y_%H:%M:%S")
    if debug:
        logging.basicConfig(filename = f"/core/logs/DEBUG_LOG-{initialisation_time}", level=logging.DEBUG)
    else:
        logging.basicConfig(filename=f"/core/logs/LOG-{initialisation_time}", level=logging.WARNING)
    logging.info(f'Logging started @ {datetime.now().strftime("%H:%M:%S")}')


def structure_check(dir):
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
            f = open(dir + "/cache/.gitignore","w+")
            f.write("""*\n!.gitignore""")
            f.close()
            logging.info("Regeneration of cache files successful.")
        except Exception as e:
            logging.critical(f"Regeneration of cache directory failed. Program is unable to cache files - exiting.")
            logging.error(f"Internal error - {e}")
            exit(126)

            # Exit code 126 - Cannot execute.
            # Attempting to run the mainthread past a structure check point would raise a DirectoryNotFound error
            # So it's more practical to log a message that makes sense and just exit with an error code.

    if not exists(dir + "/user_files"):
        logging.warning("No user_files directory found, possibly deleted by user. Regenerating...")
        try:
            makedirs(dir + "/cache")
            f = open(dir + "/cache/.gitignore","w+")
            f.write("""*\n!.gitignore""")
            f.close()
            logging.info("Regeneration of user_files successful.")
        except Exception as e:
            logging.error(f"Regeneration failed:")
            logging.error(f"Internal error - {e}")

            # Program works fine without this user_files directory access, however this could cause issues in saving
            # or loading.

    if not exists(dir + "/samples"):

        # No point regenerating this as it'd have to be cloned from the repo and that requires git to be installed.
        # Could do a check for git on PATH then use a dialogue box?
        # Kinda pointless though, samples are bundled into the repository anyway so the user has either deleted them
        # or the installation hasn't gone well

        logging.warning("No samples found, possibly deleted by user.")


def parse_eq(text: str) -> Callable:
    """
    Converts a stringed expression to a callable. params just start with %
    """
    text = text.split("%") #["blah blah"]
    

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

    logging.critical("Internal Error - RangeError")


class Color:
    """
    Class that manages RGBA values, and blending of colors
    """
    def __init__(self, red: int, green: int, blue: int, alpha: int):
        self.alpha, self.red, self.blue, self.green = alpha, red, blue, green

    def __add__(self, other):
        new_alpha = self.alpha/255+ other.alpha/255*(1-self.alpha/255)
        result = Color(min(floor((self.red/255   * self.alpha/255 + other.red/255   * other.alpha/255) * 255), 255),
                       min(floor((self.green/255 * self.alpha/255 + other.green/255 * other.alpha/255) * 255), 255),
                       min(floor((self.blue/255  * self.alpha/255 + other.blue/255  * other.alpha/255) * 255), 255),
                       floor(new_alpha * 255))
        return result
    

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
            logging.ERROR("Gradient object received invalid index.")
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
        logging.debug(f"Saving colormap to {path}")
        data = self._gradient._color_peaks[:] #protected access is fine as it is a copy
        if path[-1] != "/":
            file = open(path+".colormap", "w", encoding="utf-8")
        else:
            files_in_dir = [file for file in listdir(path) if isfile(join(path, file))]                       #list files in dir
            filtered_files = list(filter(lambda x:"unnamed_colormap" in x, files_in_dir))                     #filter unnamed_colormap-like files
            file = open(path+f'/unnamed_colormap_{len(filtered_files)}.colormap', encoding="utf-8")           #create a new colormap without overwriting existing ones (hopefully)
        for color, pos in data:
            file.write(f'{color.red}, {color.green}, {color.blue}, {color.alpha} @ {pos}')
            file.write("\n")
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
    
    