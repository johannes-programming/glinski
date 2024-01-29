# imports
from __future__ import annotations

from enum import Enum, IntEnum
from typing import Generator, Iterable, List, Self, Tuple, Union

import upcounting
from isometric import Vector

from .pieces import *
from .players import *

# __all__
__all__ = [
    'Cell',
    'File',
]




# class
class Color(Enum):
    LIGHT = 1.0
    MEDIUM = 0.5
    DARK = 0.0
    def turntable(self):
        cls = type(self)
        ans = {
            cls.LIGHT:cls.DARK,
            cls.MEDIUM:cls.MEDIUM,
            cls.DARK:cls.LIGHT,
        }[self]
        return ans




# File
class File(IntEnum):
    (a, b, c, d, e, f, g, h, i, k, l) = range(11)
    def __getitem__(self, rank:int) -> Cell:
        if type(rank) is not int:
            raise TypeError(rank)
        return Cell[self.name + str(rank)]
    def __iter__(self):
        return (self[n + 1] for n in range(len(self)))
    def __len__(self) -> int:
        return 11 - abs(self - 5)
    def turntable(self) -> Self:
        cls = type(self)
        ans = cls(10 - self)
        return ans




# Cell
class Cell(IntEnum):
    # fields
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
    ) = range(91)

    
    # protected
    @classmethod
    def _setup(cls):
        cls.Color = Color
        for o in cls:
            x = min(0, 5 - o.file)
            y = min(0, o.file - 5)
            z = o.rank - 6
            o._VECTOR = Vector(x=x, y=y, z=z)
            o._COLOR = Color(((1 - x - y - z) % 3) / 2)
            o._TEXT_POSITION = 5 - x + y, 10 + x + y - z - z
            o._HFLIP = o.file.turntable()[o.rank]
            height = len(o.file)
            o._VFLIP = o.file[height + 1 - o.rank]
        cls._BY_VECTOR = dict()
        for o in cls:
            cls._BY_VECTOR[o._VECTOR] = o
        for y in range(0, 1):
            for o in cls:
                u = Vector(x=1, y=y)
                rays = list()
                for direction in range(6):
                    v = u.rotate(direction)
                    ray = list()
                    for skip in upcounting.count_up():
                        try:
                            c = o.apply((skip + 1) * v)
                        except:
                            break
                        else:
                            ray.append(c)
                    ray = tuple(ray)
                    rays.append(ray)
                rays = tuple(rays)
                if y:
                    o._DIAGONAL_RAYS = rays
                else:
                    o._AXIAL_RAYS = rays
        
        
                    


        blackdraft = dict(
            c8 = Piece.r,
            d9 = Piece.n,
            e10 = Piece.q,
            f9 = Piece.b,
            f10 = Piece.b,
            f11 = Piece.b,
            g10 = Piece.k,
            h9 = Piece.n,
            i8 = Piece.r,
            b7 = Piece.p,
            c7 = Piece.p,
            d7 = Piece.p,
            e7 = Piece.p,
            f7 = Piece.p,
            g7 = Piece.p,
            h7 = Piece.p,
            i7 = Piece.p,
            k7 = Piece.p,
        )
        for o in cls:
            o._NATIVE = None
        for k, v in blackdraft.items():
            cls[k]._NATIVE = v
            cls[k]._VFLIP._NATIVE = v.turntable()
        

    # conversion
    @property
    def fen(self) -> str:
        return self.name
    @classmethod
    def by_fen(cls, value:str, /) -> Self:
        value = str(value).lower()
        if value == '-':
            return None
        return cls[value]
    @property
    def flag(self) -> int:
        return 1 << self
    @classmethod
    def by_flag(cls, value, /):
        v = int(value)
        for ans in cls:
            if ans.flag == v:
                return ans
        raise ValueError(value)
    @property
    def uci(self) -> str:
        return self.name
    @classmethod
    def by_uci(cls, value:str, /):
        return cls[str(value).lower()]
    @property
    def file(self) -> File:
        return File[self.name[0]]
    @property
    def rank(self) -> int:
        return int(self.name[1:])
    @classmethod
    def by_file_and_rank(cls, 
        file:File, 
        rank:int,
    ) -> Self:
        return File(file)[rank]

    
    # public
    def apply(self, vector:Vector) -> Self:
        cls = type(self)
        if type(vector) is not Vector:
            raise TypeError(vector)
        w = self._VECTOR + vector
        ans = cls._BY_VECTOR[w]
        return ans
    def axial_ray(self, direction:int) -> Tuple[Self]:
        return self._AXIAL_RAYS[direction % 6]
    @property
    def color(self) -> Color:
        return self._COLOR
    def count_up(self, *, 
        vector:Vector,
        start:int=0,
        stop=None,
    ) -> Generator[
        Tuple[int, Self],
        None,
        None,
    ]:
        cls = type(self)
        if type(vector) is not Vector:
            raise TypeError(vector)
        for n in upcounting.count_up(start, stop):
            try:
                yield n, cls._BY_VECTOR[self._VECTOR]
            except KeyError:
                return
            else:
                v += vector
    def diagonal_ray(self, direction:int) -> Tuple[Self]:
        return self._DIAGONAL_RAYS[direction % 6]
    def hflip(self) -> Self:
        return self._HFLIP
    def native(self) -> Union[Piece, None]:
        return self._NATIVE
    def search(self, 
        vectors:Iterable[Vector],
    ) -> List[Self]:
        cls = type(self)
        vectors = list(vectors)
        ans = list()
        for v in vectors:
            if type(v) is not Vector:
                raise TypeError(v)
            w = self._VECTOR + v
            try:
                other_cell = cls._BY_VECTOR[w]
            except:
                continue
            else:
                ans.append(other_cell)
        return ans
    def slide(self, 
        vector:Vector
    ) -> Generator[Self, None, None]:
        cls = type(self)
        if type(vector) is not Vector:
            raise TypeError(vector)
        u = self._VECTOR
        while True:
            u += vector
            try:
                yield cls._BY_VECTOR[u]
            except:
                break
    def text_position(self) -> Tuple[int, int]:
        return self._TEXT_POSITION
    def turntable(self):
        cls = type(self)
        value = int(self)
        value = 90 - value
        ans = cls(value)
        return ans
    def vector_from(self, other:Self) -> Vector:
        cls = type(self)
        other = cls(other)
        ans = self._VECTOR - other._VECTOR
        return ans
    def vector_to(self, other:Self) -> Vector:
        return -self.vector_from(other)
    def vflip(self) -> Self:
        return self._VFLIP


Cell._setup()


