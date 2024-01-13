import typing
from enum import IntFlag

from .cells import *
from .cli import *

# __all__
__all__ = ['BitBoard']

CENTER_FLAG = 1 << 45
LOWER_MASK = CENTER_FLAG - 1
UPPER_MASK = LOWER_MASK << 46

class BitBoard(IntFlag):

    # cells
    def cells(self) -> typing.Set[Cell]:
        ans = set()
        for cell in Cell:
            if (self & cell.flag):
                ans.add(cell)
        return ans
    @classmethod
    def by_cells(cls, *cells) -> typing.Self:
        ans = 0
        for c in cells:
            ans |= Cell(c).flag
        ans = cls(ans)
        return ans
    

    
    # methods
    #   public
    def bitneg(self) -> typing.Self:
        cls = type(self)
        ans = 0
        for cell in Cell:
            if not (self & cell.flag):
                ans |= cell.flag
        ans = cls(ans)
        return ans

    def swapplayer(self) -> typing.Self:
        cls = type(self)
        upper = self & UPPER_MASK
        center = self & CENTER_FLAG
        lower = self & LOWER_MASK
        ans = 0
        ans |= (upper >> 46)
        ans |= center
        ans |= (lower << 46)
        ans = cls(ans)
        return ans
    
    def text(self) -> str:
        symbols = ['.'] * 91
        for cell in Cell:
            if self & cell.flag:
                symbols[cell] = '1'
        ans = cli.text(symbols)
        return ans


