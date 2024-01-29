# imports
from enum import IntEnum
from typing import Self

from .strangeFuncs import *

# __all__
__all__ = ['Player']




# class
class Player(IntEnum):
    #fields
    WHITE = 0
    BLACK = 1
    # setup
    @classmethod
    def _setup(cls):
        cls.__new__ = strangeFuncs.IntModNew(
            cls.__new__,
            modulus=2,
        )
        cls.__invert__ = cls.turntable
    # conversion
    @property
    def fen(self) -> str:
        return self.name[0].lower()
    @classmethod
    def by_fen(cls, value:str, /):
        if type(value) is not str:
            raise TypeError(value)
        for item in cls:
            if item.fen == value:
                return item
        raise ValueError(value)
    # others
    def turntable(self) -> Self:
        cls = type(self)
        value = 1 - self.value
        ans = cls(value)
        return ans
Player._setup()
