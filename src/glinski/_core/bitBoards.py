# imports
from __future__ import annotations

import typing
from enum import IntFlag

from .cells_and_files import *
from .cli import *
from .strangeFuncs import *

# __all__
__all__ = ['BitBoard']


def flags():
    return [2 ** n for n in range(91)]

# class
class BitBoard(IntFlag):
    #
    (
        a1, a2, a3, a4, a5, a6, 
        b1, b2, b3, b4, b5, b6, b7,
        c1, c2, c3, c4, c5, c6, c7, c8,
        d1, d2, d3, d4, d5, d6, d7, d8, d9,
        e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
        f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11,
        g1, g2, g3, g4, g5, g6, g7, g8, g9, g10,
        h1, h2, h3, h4, h5, h6, h7, h8, h9,
        i1, i2, i3, i4, i5, i6, i7, i8,
        k1, k2, k3, k4, k5, k6, k7, 
        l1, l2, l3, l4, l5, l6, 
    ) = flags()
    #
    @classmethod
    def _setup(cls):
        cls.__new__ = strangeFuncs.IntModNew(
            cls.__new__, 
            modulus=2**91,
        )
    # 
    @property
    def cells(self) -> typing.Set[Cell]:
        ans = set()
        for cell in Cell:
            if (self & cell.flag):
                ans.add(cell)
        return ans
    @classmethod
    def by_cells(cls, 
        value:typing.Iterable[Cell], /,
    ) -> typing.Self:
        value = list(value)
        ans = 0
        for c in value:
            ans |= Cell(c).flag
        ans = cls(ans)
        return ans
    def text(self) -> str:
        symbols = ['.'] * 91
        for cell in Cell:
            if self & cell.flag:
                symbols[cell] = '1'
        ans = cli.text(symbols)
        return ans
    def turntable(self) -> typing.Self:
        cls = type(self)
        integer = int(self)
        binary = '{:091b}'.format(integer)
        binary = binary[::-1]
        integer = int(binary, 2)
        ans = cls(integer)
        return ans
BitBoard._setup()
