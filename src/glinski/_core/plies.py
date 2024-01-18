# imports
import string
import typing
from dataclasses import dataclass

from isometric import Vector

from .cells import *
from .pieces import *
from .players import *

# __all__
__all__ = ['Ply']




# classes
@dataclass(frozen=True)
class BasePly:
    # fields
    from_cell:Cell
    to_cell:Cell
    promotion:typing.Optional[Piece.Kind]
    
class Ply(BasePly):
    # methods
    #   dunder
    def __abs__(self):
        return abs(self.vector())
    def __bool__(self):
        return not self.is_null()
    def __init__(self, *,
        from_cell:Cell,
        to_cell:Cell,
        promotion:typing.Optional[Piece.Kind],
    ) -> None:
        from_cell = Cell(from_cell)
        to_cell = Cell(to_cell)
        if promotion is not None:
            promotion = Piece.Kind(promotion)
        super().__init__(
            from_cell=from_cell,
            to_cell=to_cell,
            promotion=promotion,
        )
    def __repr__(self) -> str:
        return self.uci
    def __str__(self) -> str:
        return self.uci

    #   public
    #     conversion
    @property
    def uci(self) -> typing.Self:
        if self.is_null():
            return "0000"
        ans = ""
        ans += self.from_cell.name
        ans += self.to_cell.name
        if self.promotion is not None:
            ans += self.promotion.uci
        return ans
    @classmethod
    def by_uci(cls, value:str) -> typing.Optional[typing.Self]:
        value = str(value)
        if value == "0000":
            return cls.null()
        value = value.lower()
        if value[-1] in string.digits:
            promotion = None
        else:
            promotion = Piece.Kind.by_uci(value[-1])
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
    
    #     others
    def intermediates(self) -> typing.List[Cell]:
        w = self.vector().factorize()[1]
        c = self.from_cell
        ans = list()
        while True:
            c = c.apply(w)
            if c != self.to_cell:
                ans.append(c)
            else:
                break
        return ans
    
    def is_null(self) -> bool:
        if self.from_cell != 0:
            return False
        if self.to_cell != 0:
            return False
        if self.promotion is not None:
            return False
        return True
    @classmethod
    def null(cls):
        return cls(
            from_cell=0,
            to_cell=0,
            promotion=None,
        )
    def suspects(self) -> typing.Set[Piece]:
        if self.from_cell == self.to_cell:
            return set()
        if self.promotion is not None:
            if self.promotion in {
                Piece.Kind.PAWN, 
                Piece.Kind.KING,
            }:
                return set()
            if abs(self.vector()) != 1:
                return set()
            if self.from_cell.promotion() is not None:
                return set()
            p = self.to_cell.promotion()
            if p is None:
                return set()
            return {Piece(6 * p)}
        v = self.vector()
        n, w = v.factorize()
        a = float(abs(w))
        digest = w.digest()
        ans = set()
        if a == 7 ** .5:
            if n == 1:
                ans |= {Piece.n, Piece.N}
        if a == 3 ** .5:
            ans = {Piece.b, Piece.B, Piece.q, Piece.Q}
            if n == 1:
                ans |= {Piece.k, Piece.K}
        if a == 1 ** .5:
            ans = {Piece.r, Piece.R, Piece.q, Piece.Q}
            if (n == 2) and (digest.x == 0):
                native = self.from_cell.native()
                if digest.y > 0:
                    if native == Piece.P:
                        ans.add(native)
                if digest.y < 0:
                    if native == Piece.p:
                        ans.add(native)
            if n == 1:
                ans |= {Piece.k, Piece.K}
                if digest.y > 0:
                    ans.add(Piece.P)
                if digest.y < 0:
                    ans.add(Piece.p)
        return ans
            
    def vector(self) -> Vector:
        return self.from_cell.vector_to(self.to_cell)








    