# imports
from __future__ import annotations

from enum import IntFlag
from itertools import combinations
from typing import Any, Iterable, List, Self, Set, Tuple

from .cells_and_files import *
from .cli import *
from .strangeFuncs import *
from .pieces import *
from isometric import Vector

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
    def _axial_attacks(self, origin):
        cls = type(self)
        ans = cls(0)
        origin = Cell(origin)
        for i in range(6):
            block = self & cls._axial_mask(origin, direction=i)
            gap = cls._axial_gap(origin, block=block)
            ans |= cls._axial_mask(origin, direction=i, gap=gap)
        return ans
    @classmethod
    def _axial_mask(cls, origin, *, direction=None):
        if direction is None:
            return cls._AXIAL_BLOCK[origin]
        return cls._AXIAL[origin][direction]
    def _diagonal_attacks(self, origin):
        cls = type(self)
        ans = cls(0)
        origin = Cell(origin)
        for i in range(6):
            block = self & cls._diagonal_mask(origin, direction=i)
            gap = cls._diagonal_gap(origin, block=block)
            ans |= cls._diagonal_mask(origin, direction=i, gap=gap)
        return ans
    @classmethod
    def _diagonal_mask(cls, origin, *, direction=None):
        if direction is None:
            return cls._DIAGONAL_BLOCK[origin]
        return cls._DIAGONAL[origin][direction]
    @classmethod
    def _env(cls, *units, origin, rotate):
        origin = Cell(origin)
        rotate = bool(rotate) * 5 + 1
        rotate = list(range(rotate))
        ans = cls(0)
        for unit in units:
            hands = [unit, unit.hflip()]
            for hand in hands:
                for steps in rotate:
                    v = hand.rotate(steps)
                    try:
                        cell = origin.apply(v)
                    except:
                        continue
                    ans |= cell.flag
        return ans
    @classmethod
    def _envs(cls, *args, **kwargs):
        ans = list()
        for c in range(91):
            env = cls._env(*args, origin=c, **kwargs)
            ans.append(env)
        ans = tuple(ans)
        return ans
    def _masksgap(self, 
        origin:Cell, 
        mask:Self,
    ) -> int:
        cls = type(self)
        origin = Cell(origin)
        key = mask & self
        ans = cls._GAPS_BY_ORIGIN[origin][key]
        return ans
    @classmethod
    def _gaps(cls, origin:Cell):
        ans = dict()
        for y in range(2):
            if y:
                rays = origin.diagonal_ray
            else:
                rays = origin.axial_ray
            for i in range(6):
                ans.update(cls._raygaps(rays(i)))
        return ans
    @classmethod
    def _powerset(s):
        s = set(s)
        ans = set()
        for r in range(len(s) + 1):
            ans.update(combinations(s, r))
        return ans
    @classmethod
    def _raygaps(cls, ray:Tuple[Cell]):
        ans = dict()
        for value, closest in enumerate(ray):
            options = ray[value + 1:]
            for comb in cls._powerset(options):
                cells = {closest} | set(comb)
                key = cls.by_cells(cells)
                ans[key] = value
        return ans
    @classmethod
    def _setup(cls):
        #
        cls.__new__ = strangeFuncs.IntModNew(
            cls.__new__, 
            modulus=2**91,
        )
        #
        cls._ENVS_FOR_KNIGHT = cls._envs(
            Vector(x=2, y=1),
            rotate=True,
        )
        cls._ENVS_FOR_KING = cls._envs(
            Vector(x=1),
            Vector(x=1, y=1),
            rotate=True,
        )
        cls._ENVS_FOR_P = cls._envs(
            Vector(x=-1),
            rotate=False,
        )
        cls._ENVS_FOR_p = cls._envs(
            Vector(x=1),
            rotate=False,
        )
        #
        for y in range(2):
            mmmm = list()
            for c in range(91):
                o = Cell(c)
                if y:
                    rays = o.diagonal_ray
                else:
                    rays = o.axial_ray
                mmm = list()
                for i in range(6):
                    ray = rays(i)
                    mm = list()
                    for j in range(len(ray) + 1):
                        m = cls.by_cells(ray[:j])
                        mm.append(m)
                    mm = tuple(mm)
                    mmm.append(mm)
                mmm = tuple(mmm)
                mmmm.append(mmm)
            mmmm = tuple(mmmm)
            if y:
                cls._DIAGONAL = mmmm
            else:
                cls._AXIAL = mmmm
        #
        cls._GAPS_BY_ORIGIN = [None] * 91
        for o in Cell:
            me = {cls(0):-1}
            rays = list()
            for i in range(6):
                rays.append(o.axial_ray(i))
                rays.append(o.diagonal_ray(i))
            for ray in rays:
                me.update(cls._raygaps(ray))
            cls._GAPS_BY_ORIGIN[o] = me



                

    # 
    @property
    def cells(self) -> Set[Cell]:
        ans = set()
        for cell in Cell:
            if (self & cell.flag):
                ans.add(cell)
        return ans
    @classmethod
    def by_cells(cls, 
        value:Iterable[Cell], /,
    ) -> Self:
        value = list(value)
        ans = 0
        for c in value:
            ans |= Cell(c).flag
        ans = cls(ans)
        return ans
    
    #
    def attacks(self, cell, piece) -> Self:
        cls = type(self)
        cell = Cell(cell)
        piece = Piece(piece)
        kind = piece.kind
        free = ~self
        if piece == Piece.P:
            return cls._ENVS_FOR_P[cell] & ~free
        if piece == Piece.p:
            return cls._ENVS_FOR_p[cell] & ~free
        if kind == Piece.Kind.KNIGHT:
            return cls._ENVS_FOR_KNIGHT[cell] & ~free
        if kind == Piece.Kind.KING:
            return cls._ENVS_FOR_KING[cell] & ~free
        ans = cls(0)
        if kind != Piece.Kind.ROOK:
            ans |= self._diagonal_attacks(cell)
        if kind != Piece.Kind.BISHOP:
            ans |= self._axial_attacks(cell)
        return ans

        

    @classmethod
    def axial_mask(cls, 
        origin, *,
        direction:int,
        gap:int=-1,
    ) -> Tuple[Self]:
        origin = Cell(origin)
        direction %= 6
        ans = cls._AXIAL[origin][direction][gap]
        return ans
    def axial_gap(self, 
        origin, *, 
        direction,
    ) -> int:
        return self._masksgap(
            origin,
            self.axial_mask(direction),
        )
    @classmethod
    def diagonal_mask(cls, 
        origin, *,
        direction:int,
        gap:int=-1,
    ) -> Tuple[Self]:
        origin = Cell(origin)
        direction %= 6
        ans = cls._DIAGONAL[origin][direction][gap]
        return ans
    def diagonal_gap(self, 
        origin, *, 
        direction,
    ) -> int:
        return self._masksgap(
            origin, 
            self.diagonal_mask(direction),
        )
    def text(self) -> str:
        symbols = ['.'] * 91
        for cell in Cell:
            if self & cell.flag:
                symbols[cell] = '1'
        ans = cli.text(symbols)
        return ans
    def turntable(self) -> Self:
        cls = type(self)
        integer = int(self)
        binary = '{:091b}'.format(integer)
        binary = binary[::-1]
        integer = int(binary, 2)
        ans = cls(integer)
        return ans
    
BitBoard._setup()
