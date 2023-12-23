import typing

from glinski._enums import *

__all__ = ['Move']

class Move(typing.NamedTuple):
    start:Cell
    stop:Cell
    promotion:typing.Union[PieceType, None]
    def __post_init__(self, *args, **kwargs):
        if type(self.start) is not Cell:
            raise TypeError(self.start)
        if type(self.stop) is not Cell:
            raise TypeError(self.stop)
        if self.promotion is None:
            return
        if type(self.promotion) is not PieceType:
            raise TypeError(self.promotion)

