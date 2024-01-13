from __future__ import annotations

import typing
from enum import IntEnum

import upcounting
from isometric import Vector

from .colors import *
from .pieces import *
from .players import *

# __all__
__all__ = [
    'Cell',
    'File',
]


# global variables
NATIVES = None
VECTORS = None
CELLS_BY_VECTOR = None
HFLIP = None
VFLIP = None


# File
class File(IntEnum):
    a = 0
    b = 1
    c = 2
    d = 3
    e = 4
    f = 5
    g = 6
    h = 7
    i = 8
    k = 9
    l = 10
    def _pawnstart(self, player:Player) -> int:
        if type(player) is not Player:
            raise TypeError(player)
        if player == Player.WHITE:
            return self.height() - 6
        else:
            return 7
    def cell(self, rank:int) -> Cell:
        if type(rank) is not int:
            raise TypeError(rank)
        return Cell[self.name + str(rank)]
    def ep_cell(self, player:Player) -> Cell:
        rank = self._pawnstart(player.opponent())
        if player == Player.BLACK:
            rank += 1
        else:
            rank -= 1
        ans = self.cell(rank)
        return ans
    def height(self) -> int:
        return 11 - abs(self - 5)
    def pawnstart(self, player:Player) -> Cell:
        rank = self._pawnstart(player)
        ans = self.cell(rank)
        return ans
    def promotion(self, player:Player) -> Cell:
        if type(player) is not Player:
            raise TypeError(player)
        if player == Player.BLACK:
            rank = 1
        else:
            rank = self.height()
        ans = self.cell(rank)
        return ans
    def swapplayer(self):
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
    ) = list(range(46)) + list(range(90, 45, -1))
    
    # methods
    #   public
    #     conversion
    #       fen
    @property
    def fen(self) -> str:
        return self.name
    @classmethod
    def by_fen(cls, value:str, /) -> typing.Self:
        value = str(value)
        if value == '-':
            return None
        return cls[value]
    #       flag
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
    #       file and rank
    @property
    def file(self) -> File:
        return File[self.name[0]]
    @property
    def rank(self) -> int:
        return int(self.name[1:])
    @classmethod
    def by_file_and_rank(cls, file:File, rank:int) -> typing.Self:
        file = File(file)
        rank = int(rank)
        name = file.name + str(rank)
        ans = cls(name)
        return ans

    
    #     other
    def apply(self, 
        vector:Vector,
    ) -> typing.Self:
        if type(vector) is not Vector:
            raise TypeError(vector)
        w = VECTORS[self] + vector
        ans = CELLS_BY_VECTOR[w]
        return ans
    @property
    def color(self) -> Color:
        desc = self.value.description()
        residue = (sum(desc) + 1) % 3
        value = residue / 2
        ans = Color(value)
        return ans
    def count_up(self, *, 
        vector:Vector,
        start:int=0,
        stop=None,
    ) -> typing.Generator[
        typing.Tuple[int, typing.Self],
        None,
        None,
    ]:
        if type(vector) is not Vector:
            raise TypeError(vector)
        v = VECTORS[self]
        for n in upcounting.count_up(start, stop):
            try:
                yield n, CELLS_BY_VECTOR[v]
            except KeyError:
                return
            else:
                v += vector
    def hflip(self) -> typing.Self:
        return HFLIP[self]
    def native(self) -> typing.Union[Piece, None]:
        return NATIVES[self]
    def pawn_legal(self, player:Player) -> bool:
        if type(player) is not Player:
            raise TypeError(player)
        if self.promotion(player):
            return False
        if player == Player.WHITE:
            return self.rank >= self.file.height() - 6 
        else:
            return self.rank <= 7
    def promotion(self, 
        player:typing.Optional[Player]=None,
    ) -> typing.Union[bool, typing.Optional[Player]]:
        if player is not None:
            return self == self.file.promotion(player)
        for player in Player:
            if self == self.file.promotion(player):
                return player
        return None
    def search(self, 
        vectors:typing.Iterable[Vector],
    ) -> typing.List[typing.Self]:
        ans = list()
        u = VECTORS[self]
        for v in vectors:
            if type(v) is not Vector:
                raise TypeError(v)
            try:
                other_cell = CELLS_BY_VECTOR[u + v]
            except:
                continue
            else:
                ans.append(other_cell)
        return ans
    def slide(self, vector:Vector) -> typing.Generator[typing.Self, None, None]:
        if type(vector) is not Vector:
            raise TypeError(vector)
        u = VECTORS[self]
        while True:
            u += vector
            try:
                yield CELLS_BY_VECTOR[u]
            except:
                break
    def swapplayer(self):
        cls = type(self)
        if self < 45:
            ans = cls(self + 46)
        elif self > 45:
            ans = cls(self - 46)
        else:
            ans = self
        return ans
    def text_position(self) -> typing.Tuple[int, int]:
        desc = VECTORS[self].description()
        x = 5 + desc.y
        y = 10 + desc.y - desc.z - desc.z
        ans = x, y
        return ans
    def vector_from(self, other:typing.Self) -> Vector:
        return VECTORS[self] - VECTORS[other]
    def vector_to(self, other:typing.Self) -> Vector:
        return -self.vector_from(other)
    def vflip(self) -> typing.Self:
        return VFLIP[self]
def vectors():
    ans = [None] * 91
    for cell in Cell:
        x = min(0, 5 - cell.file)
        y = min(0, cell.file - 5)
        z = cell.rank - 6
        v = Vector(x=x, y=y, z=z)
        ans[cell] = v
    return ans
VECTORS = vectors()
def cells_by_vector():
    ans = dict()
    for i, v in enumerate(VECTORS):
        ans[v] = Cell(i)
    return ans
CELLS_BY_VECTOR = cells_by_vector()
def hflip():
    ans = [None] * 91
    for cell in Cell:
        u = VECTORS[cell]
        v = u.hflip()
        for other_cell in Cell:
            if v == VECTORS[other_cell]:
                ans[cell] = other_cell
                break
    return ans
HFLIP = hflip()
def vflip():
    ans = [None] * 91
    for cell in Cell:
        u = VECTORS[cell]
        v = u.vflip()
        for other_cell in Cell:
            if v == VECTORS[other_cell]:
                ans[cell] = other_cell
                break
    return ans
VFLIP = vflip()
def natives() -> typing.Dict[str, str]:
    blackdraft = dict()
    blackdraft['c8'] = 'r'
    blackdraft['d9'] = 'n'
    blackdraft['e10'] = 'q'
    blackdraft['f9'] = 'b'
    blackdraft['f10'] = 'b'
    blackdraft['f11'] = 'b'
    blackdraft['g10'] = 'k'
    blackdraft['h9'] = 'n'
    blackdraft['i8'] = 'r'
    blackdraft['b7'] = 'p'
    blackdraft['c7'] = 'p'
    blackdraft['d7'] = 'p'
    blackdraft['e7'] = 'p'
    blackdraft['f7'] = 'p'
    blackdraft['g7'] = 'p'
    blackdraft['h7'] = 'p'
    blackdraft['i7'] = 'p'
    blackdraft['k7'] = 'p'
    ans = [None] * 91
    for k, v in blackdraft.items():
        blackcell = Cell[k]
        ans[blackcell] = Piece[v]
        whitecell = blackcell.vflip()
        ans[whitecell] = ans[blackcell].swapplayer()
    return ans
NATIVES = natives()





