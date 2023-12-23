import typing
from collections import namedtuple

from glinski import _consts
from glinski._enums import *
from glinski._namedtuples.Arrival import Arrival

# __all__
__all__ = ['Arrangement']



# Arrangement
def cellnames() -> typing.List[str]:
    ans = [cell.name for cell in Cell]
    ans.sort()
    return ans
BaseArrangement = namedtuple(
    typename='BaseArrangement', 
    field_names=cellnames(),
    defaults=[None] * len(Cell),
)
class Arrangement(BaseArrangement):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        for item in self:
            if item is None:
                continue
            if type(item) is not PieceKind:
                raise TypeError(item)
            
    def _check(self, cellname) -> bool:
        currentKing = getattr(self, cellname)
        currentPlayer = currentKing.player()
        if currentPlayer == Player.WHITE:
            pawnArrival = _consts.arrivals.BLACK_PAWN_ATTACK
        else:
            pawnArrival = _consts.arrivals.WHITE_PAWN_ATTACK
        arrivals = [
            pawnArrival,
            _consts.arrivals.HORSEJUMP,
            _consts.arrivals.DIAGONAL,
            _consts.arrivals.FILE,
        ]
        for arrival in arrivals:
            if self._check_arrival(
                arrival=arrival, 
                cellname=cellname,
            ):
                return True
        return False

    def _check_arrival(self, 
        arrival:Arrival,
        *, 
        cellname:str,
    ) -> bool:
        currentPlayer = getattr(self, cellname).player()
        for direction in arrival.directions():
            for cell, pieceTypes in direction:
                pieceKind = getattr(self, cell.name)
                if pieceKind is None:
                    continue
                if pieceKind.player() == currentPlayer:
                    break
                if pieceKind.pieceType() in pieceTypes:
                    return True
        return False


    def check(self, currentPlayer:Player) -> bool:
        currentKing = PieceType.KING.pieceKind(currentPlayer)
        for cellname, pieceKind in self._asdict().items():
            if pieceKind is None:
                continue
            if pieceKind != currentKing:
                continue
            if self._check(cellname):
                return True
        return False

    def count(self, *values):
        ans = 0
        for x in self:
            ans += int(x in values)
        return ans

    def invert(self) -> typing.Self:
        cls = type(self)
        kwargs = dict()
        for selfkey, selfvalue in self._asdict().items():
            selfcell = Cell[selfkey]
            selfvector = selfcell.value
            ansvector = selfvector.vflip()
            anscell = Cell[ansvector]
            anskey = anscell.name
            ansvalue = selfvalue.invert()
            kwargs[anskey] = ansvalue
        ans = cls(**kwargs)
        return ans

    @classmethod
    def native(cls) -> typing.Self:
        kwargs = dict()
        for cell in Cell:
            kwargs[cell.name] = cell.native()
        ans = cls(**kwargs)
        return ans


    def text(self, *, hpad=3, vpad=0, unicode=False) -> str:
        empty = [" "] * 11
        hspacer = " " * hpad
        emptyline = hspacer.join(hspacer)
        vspacer = emptyline.join(['\n'] * (vpad + 1))
        table = [list(empty) for i in range(21)]
        for cell in Cell:
            desc = cell.value.description()
            i = 5 + desc.y
            j = 10 + desc.y - desc.z - desc.z
            pieceKind = self.get(cell)
            if pieceKind is None:
                s = '.'
            elif unicode:
                s = pieceKind.value
            else:
                s = pieceKind.name
            table[j][i] = s
        lines = [hspacer.join(row) for row in table]
        ans = vspacer.join(lines)
        return ans

