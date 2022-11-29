from math import floor

def _edit(inner):
    """
    Decorator for Point that manages the amount of times it has been edited
    """
    def outer(*args):
        args[0]._edits+=1
        return inner(*args)
    return outer


class RangeError(ValueError):
    """ piss fart """


class Color:
    """
    Class that manages RGBA values, and blending of colors
    """
    def __init__(self, red: int, green: int, blue: int, alpha: int):
        self.alpha, self.red, self.blue, self.green = alpha, red, blue, green

    def __add__(self, other):
        new_alpha = self.alpha/255+ other.alpha/255*(1-self.alpha/255)
        result = Color(floor(((self.red/255* self.alpha/255+ other.red/255* other.alpha/255* (1 - self.alpha/255)) / new_alpha) * 255),
                       floor(((self.green/255* self.alpha/255+ other.green/255* other.alpha/255* (1 - self.alpha/255)) / new_alpha) * 255),
                       floor(((self.blue/255* self.alpha/255+ other.blue/255* other.alpha/255* (1 - self.alpha/255)) / new_alpha) * 255),
                       floor(new_alpha * 255))
        return result


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

    @_edit
    def brighten(self, amount) -> None:
        """
        Brightens the color of a point by adding to the alpha value (hacky ik fix later)
        """
        self._color = Color(self._color.red, self._color.green,
                            self._color.blue, min(self._color.alpha+amount, 255))

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


class Gradient:
    """
    Class that manages color gradients
    """
    def __init__(self, gradient: list):
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
                next_color = color
                prev_color = self._color_peaks[index-1][0]
                rel_pos = val-self._color_peaks[index-1][1]
                range_between = position - self._color_peaks[index-1][1]
                break
        if rel_pos is None:
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
    Encapsulates gradient for some reason
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

    def get_value(self, time) -> Color:
        """
        Returns the color at a time
        """
        return self._gradient[time]

    def __len__(self):
        return len(self._gradient)
