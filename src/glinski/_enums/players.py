import typing
from enum import Enum

from .colors import *

__all__ = ['Player']

class Player(Enum):
    BLACK = False
    WHITE = True
    def color(self) -> Color:
        return Color(float(self.value))
    def invert(self) -> typing.Self:
        cls = type(self)
        value = not self.value
        ans = cls(value)
        return ans
