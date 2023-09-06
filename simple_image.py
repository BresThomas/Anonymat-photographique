#!/usr/bin/env python3
import sys
import PIL.Image
import PIL.features
import PIL.ImageShow
from packaging import version

# check PIL version
assert version.parse(PIL.features.version('pil')) >= version.parse("8.3.2"), \
       "PIL version should be >= 8.3.2"

class Image:
    trace = True

    def __init__(self, pil_image):
        assert isinstance(pil_image, PIL.Image.Image)
        self._pil_image = pil_image

    @property
    def width(self):
        """largeur en pixels de l'image"""
        return self._pil_image.width

    @property
    def height(self):
        """hauteur en pixels de l'image"""
        return self._pil_image.height

    @property
    def definition(self):
        """definition en pixels de l'image"""
        return (self._pil_image.width, self._pil_image.height)

    def get_width(self):
        """largeur en pixels de l'image"""
        return self.width

    def get_height(self):
        """hauteur en pixels de l'image"""
        return self.height

    def get_definition(self):
        """definition en pixels de l'image"""
        return self.definition

    def _check_coordinate(self, xy):
        if (xy[0] < 0 or xy[0] >= self.width
            or xy[1] < 0 or xy[1] >= self.height):
            raise ValueError(f"Coordinate ({xy[0]},{xy[1]}) out of image {self.width}x{self.height}")

    def _check_color(self, color):
        for comp in color:
            if comp < 0 or comp > 255:
                raise IndexError(f"Color components ({color[0]},{color[1]},{color[2]}) out of range")

    def get_color(self, xy):
        self._check_coordinate(xy)
        color = self._pil_image.getpixel(xy)
        return color

    def set_color(self, xy, color):
        self._check_coordinate(xy)
        self._check_color(color)
        self._pil_image.putpixel(xy, color)

    def save(self, filepath):
        self._pil_image.save(filepath)
        self.errtrace(f"écriture d'une image"
                      f" ({self._pil_image.width}x{self._pil_image.height})"
                      f" dans le fichier '{filepath}'.")

    def show(self, title):
        PIL.ImageShow.show(self._pil_image, title=title)

    @classmethod
    def errtrace(cls, *args, **kwargs):
        if cls.trace:
            print(*args, file=sys.stderr, **kwargs)

    @classmethod
    def read(cls, filepath):
        im = Image(PIL.Image.open(filepath).convert("RGB"))
        cls.errtrace(f"lecture d'une image"
                     f" ({im.width}x{im.height})"
                     f" depuis le fichier '{filepath}'.")
        return im

    @classmethod
    def new(cls, width, height):
        im = Image(PIL.Image.new("RGB", (width, height)))
        cls.errtrace(f"nouvelle image"
                     f" ({im.width}x{im.height}).")
        return im

if __name__ == "__main__":
    PIL.features.pilinfo(supported_formats=False)
