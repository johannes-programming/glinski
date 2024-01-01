import string
import typing
from dataclasses import dataclass

from isometric import Vector

from glinski._enums import *

from .pieces import *

__all__ = ['Move']

PROMOTIONS_BY_UCI_NOTATION = dict(
    n = PieceKind.KNIGHT,
    b = PieceKind.BISHOP,
    r = PieceKind.ROOK,
    q = PieceKind.QUEEN,
)
OPTIONAL_PIECEKIND = typing.Optional[PieceKind]

def _pieces(*kinds:PieceKind):
    return {
        Piece(kind=t, player=p)
        for t in kinds
        for p in Player
    }

@dataclass(frozen=True)
class BaseMove:
    # fields
    from_cell: Cell
    to_cell: Cell
    promotion: OPTIONAL_PIECEKIND

    # methods
    #   public
    @classmethod
    def from_uci(cls, value) -> typing.Optional[typing.Self]:
        value = str(value)
        value = value.lower()
        if value == "0000":
            return None
        if value[-1] in string.digits:
            promotion = None
        else:
            promotion = PROMOTIONS_BY_UCI_NOTATION[value[-1]]
            value = value[:-1]
        if value[2] in string.digits:
            from_cell = Cell[value[:3]]
            to_cell = Cell[value[3:]]
        else:
            from_cell = Cell[value[:2]]
            to_cell = Cell[value[2:]]
        ans = cls(
            from_cell=from_cell,
            to_cell=to_cell,
            promotion=promotion,
        )
        return ans

    def suspects(self) -> typing.Set[Piece]:
        if self.promotion in {PieceKind.PAWN, PieceKind.KING}:
            return set()
        if self.promotion is not None:
            if self.from_cell.promotion() is not None:
                return set()
            p = self.to_cell.promotion()
            if p is None:
                return set()
            return {
                Piece(
                    player=p,
                    kind=PieceKind.PAWN,
                )
            }
        if self.from_cell == self.to_cell:
            return set()
        v = self.vector()
        n, w = v.factorize()
        a = float(abs(w))
        s = w.digest().y
        if a == 7 ** .5:
            if n > 1:
                return set()
            return _pieces(
                PieceKind.KNIGHT,
            )
        if a == 3 ** .5:
            ans = _pieces(
                PieceKind.BISHOP, 
                PieceKind.QUEEN,
            )
            if n > 1:
                return ans
            ans |= _pieces(PieceKind.KING)
            if s == 0:
                return ans
            p = Player(s > 0)
            if self.to_cell.promotion(p):
                return ans
            ans.add(Piece(kind=PieceKind.PAWN, player=p))
            return ans
        if a == 1 ** .5:
            ans = _pieces(
                PieceKind.ROOK, 
                PieceKind.QUEEN,
            )
            if n > 2:
                return ans
            if n == 2:
                if w.digest().x != 0:
                    return ans
                native = self.from_cell.native()
                if native is None:
                    return ans
                if native.kind != PieceKind.PAWN:
                    return ans
                if native.player != Player(w.digest().y > 0):
                    return ans
                ans.add(native)
                return ans
            ans |= _pieces(PieceKind.KING)
            p = Player(s > 0)
            if self.to_cell.promotion(p):
                return ans
            ans.add(Piece(kind=PieceKind.PAWN, player=p))
            return ans
        return set()

    def trajectory(self) -> typing.List[Cell]:
        w = self.vector().factorize()[1]
        c = self.from_cell
        ans = list()
        while c != self.to_cell:
            ans.append(c)
            c = c.apply(w)
        return ans
            
    def vector(self) -> Vector:
        return self.from_cell.vector_to(self.to_cell)







class Move(BaseMove):
    # methods
    #   dunder
    def __init__(self, *,
        from_cell:Cell,
        to_cell:Cell,
        promotion:OPTIONAL_PIECEKIND,
    ) -> None:
        for cell in (from_cell, to_cell):
            if type(cell) is not Cell:
                raise TypeError(cell)
        if promotion is not None:
            if type(promotion) is not PieceKind:
                raise TypeError(promotion)
        super().__init__(
            from_cell=from_cell,
            to_cell=to_cell,
            promotion=promotion,
        )
    def __repr__(self) -> str:
        return str(self)
    def __str__(self) -> str:
        ans = ""
        ans += self.from_cell.name
        ans += self.to_cell.name
        if self.promotion is not None:
            for k, v in PROMOTIONS_BY_UCI_NOTATION.items():
                if v == self.promotion:
                    ans += k
                    break
        return ans

    