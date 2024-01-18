# imports
import typing
from enum import IntEnum

from .colors import *

# __all__
__all__ = ['Player']




# class
class Player(IntEnum):
    BLACK = 1
    WHITE = 0

    # conversion
    @property
    def fen(self) -> str:
        return self.name[0].lower()
    @classmethod
    def by_fen(cls, value:str, /):
        if type(value) is not str:
            raise TypeError(value)
        for item in cls:
            if item.fen() == value:
                return item
        raise ValueError(value)
    
    # 
    @property
    def color(self) -> Color:
        return Color[self.name]
    def opponent(self) -> typing.Self:
        cls = type(self)
        value = 1 - self.value
        ans = cls(value)
        return ans
