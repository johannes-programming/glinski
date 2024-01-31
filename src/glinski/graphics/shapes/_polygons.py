from typing import Self, overload
from glinski.graphics._points import *
from glinski.graphics._colors import *
from ._elements import Element

class Polygon(Element):
    def __init__(self, *points, fill, outline) -> None:
        self.points = points
        self.fill = fill
        self.outline = outline
    @classmethod
    def _color(cls, value, /):
        raise NotImplementedError
    @property
    def points(self):
        return self._points
    @points.setter
    def points(self, value):
        value = [Point(p) for p in value]
        value = tuple(value)
        self._points = value
    @property
    def fill(self):
        return self._fill
    @fill.setter
    def fill(self, value, /):
        self._fill = self._color(value)
    @property
    def outline(self):
        return self._outline
    @outline.setter
    def outline(self, value, /):
        self._outline = self._color(value)

        

