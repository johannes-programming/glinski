from __future__ import annotations

import typing
from enum import Enum, IntEnum

import upcounting
from isometric import Vector

from glinski._dataholders.pieces import *

from .colors import *
from .pieces import *
from .players import *

# __all__
__all__ = [
    'Cell',
    'Column',
]


# global variables
NATIVES = dict()
CELLS = None





# Column
class Column(IntEnum):
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    k = 10
    l = 11
    def _pawnstart(self, player:Player) -> int:
        if type(player) is not Player:
            raise TypeError(player)
        if player == Player.WHITE:
            return self.height() - 6
        else:
            return 7
    def cell(self, row:int) -> Cell:
        if type(row) is not int:
            raise TypeError(row)
        return Cell[self.name + str(row)]
    def ep_cell(self, player:Player):
        row = self._pawnstart(player.invert())
        if player == Player.BLACK:
            row += 1
        else:
            row -= 1
        ans = self.cell(row)
        return ans
    def height(self) -> int:
        return 11 - abs(self.value - 6)
    def pawnstart(self, player:Player) -> Cell:
        row = self._pawnstart(player)
        ans = self.cell(row)
        return ans
    def promotion(self, player:Player) -> Cell:
        if type(player) is not Player:
            raise TypeError(player)
        if player == Player.BLACK:
            row = 1
        else:
            row = self.height()
        ans = self.cell(row)
        return ans






# Cell
class BaseCell:
    def apply(self, vector:Vector) -> typing.Self:
        cls = type(self)
        ans = cls(self.value + vector)
        return ans
    def color(self) -> Color:
        desc = self.value.description()
        residue = (sum(desc) + 1) % 3
        value = residue / 2
        ans = Color(value)
        return ans
    def column(self) -> Column:
        return Column[self.name[0]]
    def count_up(self, *, 
        vector:Vector,
        start:int=0,
        stop=None,
    ) -> typing.Generator[
        typing.Tuple[int, typing.Self],
        None,
        None,
    ]:
        cls = type(self)
        if type(vector) is not Vector:
            raise TypeError(vector)
        u = vector * start + self.value
        for n in upcounting.count_up(start, stop):
            try:
                ans = cls(u)
            except ValueError:
                return
            yield n, ans
            u += vector
    def hflip(self) -> typing.Self:
        cls = type(self)
        return cls(self.value.hflip())
    def native(self) -> typing.Union[Piece, None]:
        return NATIVES.get(self)
    def pawn_legal(self, player:Player) -> bool:
        if type(player) is not Player:
            raise TypeError(player)
        if self.promotion(player):
            return False
        if player == Player.WHITE:
            return self.row() >= self.column().height() - 6 
        else:
            return self.row() <= 7
    def promotion(self, 
        player:typing.Optional[Player]=None,
    ) -> typing.Union[bool, typing.Optional[Player]]:
        if player is not None:
            return self == self.column().promotion(player)
        for player in Player:
            if self == self.column().promotion(player):
                return player
        return None
    def row(self) -> int:
        return int(self.name[1:])
    def vector_from(self, other:typing.Self) -> Vector:
        return -self.vector_to(other)
    def vector_to(self, other:typing.Self) -> Vector:
        cls = type(self)
        if type(other) is not cls:
            raise TypeError(other)
        ans = other.value - self.value
        return ans
    def vflip(self) -> typing.Self:
        cls = type(self)
        return cls(self.value.vflip())
def celldict() -> typing.Dict[str, Vector]:
    ans = dict()
    for column in Column:
        x = min(0, 6 - column.value)
        y = min(0, column.value - 6)
        for r in range(1, column.height() + 1):
            z = r - 6
            ans[column.name + str(r)] = Vector(x, y, z)
    return ans
Cell = Enum('Cell', celldict(), type=BaseCell)


# CELLS
CELLS = tuple(Cell)

# NATIVES
def blacknatives() -> typing.Dict[str, str]:
    ans = dict()
    ans['c8'] = 'r'
    ans['d9'] = 'n'
    ans['e10'] = 'q'
    ans['f9'] = 'b'
    ans['f10'] = 'b'
    ans['f11'] = 'b'
    ans['g10'] = 'k'
    ans['h9'] = 'n'
    ans['i8'] = 'r'
    for column in Column:
        if column in [Column.a, Column.l]:
            continue
        cellname = column.pawnstart(Player.BLACK).name
        ans[cellname] = 'p'
    return ans
def natives() -> typing.Dict[Cell, Piece]:
    ans = dict()
    for k, v in blacknatives().items():
        blacksCell = Cell[k]
        blacksPiece = Piece.from_symbol(v)
        ans[blacksCell] = blacksPiece
        whitesCell = blacksCell.vflip()
        whitesPiece = blacksPiece.invert()
        ans[whitesCell] = whitesPiece
    return ans
NATIVES = natives()
for K, V in NATIVES.items():
    if V is None:
        continue
    if type(V) is not Piece:
        raise TypeError


