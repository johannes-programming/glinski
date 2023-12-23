import typing
from enum import Enum, IntEnum

from isometric import Vector

from glinski._enums.pieces import *
from glinski._enums.players import *

# __all__
__all__ = [
    'Cell', 
    'CellColor',
    'Column',
]


# globals
NATIVES = dict()
PROMOTIONSS = dict()




# CellColor
class CellColor(Enum):
    WHITE = 1.0
    GRAY = 0.5
    BLACK = 0.0





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
        if player == Player.BLACK:
            return 7
        else:
            return self.height() - 6
    def cell(self, row:int):
        return Cell[self.name + str(row)]
    def cells(self) -> type.List:
        ans = dict()
        for r in range(1, self.height() + 1):
            ans[r] = self.cell(r)
        return ans
    def height(self) -> int:
        return 11 - abs(self.value - 6)
    def pawnstart(self, player:Player):
        row = self._pawnstart(player)
        ans = Cell[self.name + str(row)]
        return ans
    def pawnpassing(self, player:Player):
        row = self._pawnstart(player)
        if player == Player.WHITE:
            row += 1
        else:
            row -= 1
        ans = Cell[self.name + str(row)]
        return ans
    def promotion(self, player:Player):
        if type(player) is not Player:
            raise TypeError(player)
        if player == Player.BLACK:
            row = 1
        else:
            row = self.height()
        return Cell[self.name + str(row)]






# Cell
class BaseCell:
    def cellColor(self) -> CellColor:
        desc = self.value.description()
        residue = (sum(desc) + 1) % 3
        value = residue / 2
        ans = CellColor(value)
        return ans
    def column(self) -> Column:
        return Column[self.name[0]]
    def hflip(self) -> typing.Self:
        cls = type(self)
        return cls(self.value.hflip())
    def native(self) -> typing.Union[PieceKind, None]:
        return NATIVES.get(self)
    def promotion(self, player:Player) -> bool:
        if type(player) is not Player:
            raise TypeError(player)
        if player == Player.WHITE:
            return self.row() == self.column().height()
        else:
            return self.row() == 1
    @classmethod
    def promotions(cls, player:Player):
        return dict(PROMOTIONSS[player])
    def row(self) -> int:
        return int(self.name[1:])
    def vflip(self) -> typing.Self:
        cls = type(self)
        return cls(self.value.vflip())
def celldict() -> dict:
    ans = dict()
    for column in Column:
        x = min(0, 6 - column.value)
        y = min(0, column.value - 6)
        for r in range(1, column.height() + 1):
            z = r - 6
            ans[column.name + str(r)] = Vector(x, y, z)
    return ans
Cell = Enum('Cell', celldict(), type=BaseCell)





# NATIVES
def blacknatives() -> dict:
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
def natives() -> dict:
    ans = dict()
    for k, v in blacknatives().items():
        blacksCell = Cell[k]
        blacksPieceKind = PieceKind[v]
        ans[blacksCell] = blacksPieceKind
        whitesCell = blacksCell.vflip()
        whitesPieceKind = blacksPieceKind.invert()
        ans[whitesCell] = whitesPieceKind
    return ans
NATIVES = natives()


def promotionss() -> typing.Dict[Player, typing.Set[Cell]]:
    ans = dict()
    for player in Player:
        ans[player] = dict()
        for column in Column:
            ans[player][column] = column.promotion(player)
    return ans
PROMOTIONSS = promotionss()
