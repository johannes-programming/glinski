# imports
from __future__ import annotations

from enum import IntFlag
from itertools import combinations
from typing import Any, Iterable, List, Self, Set, Tuple, Dict

from .cells_and_files import *
from .cli import *
from .strangeFuncs import *
from .pieces import *
from isometric import Vector
from .players import *

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
    def _attacks(self, *, is_diagonal, origin):
        cls = type(self)
        ans = cls(0)
        origin = Cell(origin)
        for i in range(6):
            reach = cls._reach(
                origin=origin, 
                direction=i,
                is_diagonal=is_diagonal,
            )
            ans |= cls._mask(
                is_diagonal=is_diagonal,
                origin=origin, 
                direction=i, 
                reach=reach,
            )
        return ans
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
    @classmethod
    def _mask(cls, *, is_diagonal, origin, direction, reach=None):
        if reach is None:
            return cls._BLOCKING[is_diagonal][origin][direction]
        return cls._MASKING[is_diagonal][origin][direction][reach]
    @classmethod
    def _powerset(s):
        s = set(s)
        ans = set()
        for r in range(len(s) + 1):
            ans.update(combinations(s, r))
        return ans
    @classmethod
    def _rayreach(cls, 
        ray:Tuple[Cell],
    ) -> Dict[Self, int]:
        ans = {cls(0):-1}
        if len(ray) == 0:
            return ans
        ray = ray[:-1]
        for i, closest in enumerate(ray):
            value = i + 1
            options = ray[value:]
            for comb in cls._powerset(options):
                cells = {closest} | set(comb)
                key = cls.by_cells(cells)
                ans[key] = value
        return ans
    def _reach(self, *, 
        is_diagonal, 
        direction, 
        origin,
    ) -> int:
        cls = type(self)
        block = self & cls._mask(
            is_diagonal=is_diagonal,
            origin=origin, 
            direction=direction,
        )
        return cls._REACHING[origin][block]
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
        mmmmm = list()
        for is_diagonal in range(2):
            mmmm = list()
            for c in range(91):
                o = Cell(c)
                if is_diagonal:
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
            mmmmm.append(mmmm)
        mmmmm = tuple(mmmmm)
        cls._MASKING = mmmmm
        #
        bbbb = list()
        for is_diagonal in range(2):
            bbb = list()
            for c in range(91):
                bb = list()
                for i in range(6):
                    if len(cls._MASKING[is_diagonal][c][i]) < 2:
                        j = -1
                    else:
                        j = -2
                    b = cls._MASKING[is_diagonal][c][i][j]
                    bb.append(b)
                bb = tuple(bb)
                bbb.append(bb)
            bbb = tuple(bbb)
            bbbb.append(bbb)
        bbbb = tuple(bbbb)
        cls._BLOCKING = bbbb
        #
        rrr = list()
        for c in range(91):
            o = Cell(c)
            rr = {cls(0):-1}
            rays = list()
            for i in range(6):
                rays.append(o.axial_ray(i))
                rays.append(o.diagonal_ray(i))
            for ray in rays:
                rr.update(cls._rayreach(ray))
            rrr.append(rr)
        rrr = tuple(rrr)
        cls._REACHING = rrr
        # 
        black_www = list()
        for c in range(91):
            cell = Cell(c)
            if cell.rank == 1:
                ww = dict()
                ww[BitBoard(0)] = BitBoard(0)
                black_www.append(ww)
                continue
            one_ahead = Cell(c - 1)
            if cell.native() != Piece.b:
                ww = dict()
                ww[BitBoard(0)] = BitBoard(one_ahead.flag)
                ww[BitBoard(one_ahead.flag)] = BitBoard(0)
                black_www.append(ww)
                continue
            two_ahead = Cell(c - 2)
            bb_null = BitBoard(0)
            bb_one = BitBoard.by_cells({one_ahead})
            bb_two = BitBoard.by_cells({two_ahead})
            bb_both = BitBoard.by_cells({one_ahead, two_ahead})
            ww[bb_null] = bb_both
            ww[bb_one] = bb_null
            ww[bb_two] = bb_one
            ww[bb_both] = bb_null
            black_www.append(ww)
        black_www = tuple(black_www)
        white_www = list()
        for c in range(91):
            ww = dict()
            for k, v in black_www[90 - c]:
                ww[k.turntable()] = v.turntable()
            white_www.append(ww)
        white_www = tuple(white_www)
        wwww = [None] * 2
        wwww[Player.WHITE] = white_www
        wwww[Player.BLACK] = black_www
        wwww = tuple(wwww)
        cls._WALKING = wwww










                

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
        if piece == Piece.P:
            return cls._ENVS_FOR_P[cell]
        if piece == Piece.p:
            return cls._ENVS_FOR_p[cell]
        if kind == Piece.Kind.KNIGHT:
            return cls._ENVS_FOR_KNIGHT[cell]
        if kind == Piece.Kind.KING:
            return cls._ENVS_FOR_KING[cell]
        ans = cls(0)
        if kind != Piece.Kind.ROOK:
            ans |= self._attacks(is_diagonal=1, origin=cell)
        if kind != Piece.Kind.BISHOP:
            ans |= self._attacks(is_diagonal=0, origin=cell)
        return ans

        

    def axial_reach(self, 
        origin, *, 
        direction,
    ) -> int:
        origin = Cell(origin)
        ans = self._reach(
            is_diagonal=0,
            direction=direction,
            origin=origin,
        )
        return ans
    def diagonal_reach(self, 
        origin, *, 
        direction,
    ) -> int:
        origin = Cell(origin)
        ans = self._reach(
            is_diagonal=1,
            direction=direction,
            origin=origin,
        )
        return ans
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
    def walks(self, cell, piece) -> Self:
        cls = type(self)
        cell = Cell(cell)
        piece = Piece(piece)
        if piece.kind != Piece.Kind.PAWN:
            ans = self.attacks(cell=cell, piece=piece)
            ans &= ~self
        mask = cls._WALKING[piece.player][cell][BitBoard(0)]
        block = self & mask
        ans = cls._WALKING[piece.player][cell][block]
        return ans

    
BitBoard._setup()
