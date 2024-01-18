# imports
from __future__ import annotations

import typing
from dataclasses import dataclass

from .errors import *
from .players import *
from .plies import *
from .positions import *
from .terminations import *

# __all__
__all__ = ['FENPosition']




@dataclass(frozen=True)
class BaseFENPosition:
    fullmove_number:int
    halfmove_clock:int
    position:Position
class FENPosition(BaseFENPosition):
    def __init__(self, 
        position:Position=Position(), *,
        fullmove_number:int=1,
        halfmove_clock:int=0,
    ):
        if type(fullmove_number) is not int:
            raise TypeError(fullmove_number)
        if type(halfmove_clock) is not int:
            raise TypeError(halfmove_clock)
        if type(position) is not Position:
            raise TypeError(position)
        super().__init__(
            fullmove_number=fullmove_number,
            halfmove_clock=halfmove_clock,
            position=position,
        )
    @property
    def fen(self) -> str:
        ans = self.position.fen
        ans += ' ' + str(self.halfmove_clock)
        ans += ' ' + str(self.fullmove_number)
        return ans
    @classmethod
    def by_fen(cls, value:str, /) -> typing.Self:
        if type(value) is not str:
            raise TypeError(value)
        *p, h, f = value.split()
        f = int(f)
        h = int(h)
        p = Position.by_fen(' '.join(p))
        ans = cls(
            fullmove_number=f,
            halfmove_clock=h,
            position=p,
        )
        return ans
    def apply(self, ply:Ply):
        cls = type(self)
        if self.position.turn == Player.BLACK:
            fullmove_number = self.fullmove_number + 1
        else:
            fullmove_number = self.fullmove_number
        if self.position.is_reversible(ply):
            halfmove_clock = self.halfmove_clock + 1
        else:
            halfmove_clock = 0
        position = self.position.apply(ply)
        ans = cls(
            fullmove_number=fullmove_number,
            halfmove_clock=halfmove_clock,
            position=position,
        )
        return ans
    def is_legal(self):
        if not (1 <= self.fullmove_number):
            return False
        if not (0 <= self.halfmove_clock <= 150):
            return False
        return self.position.is_legal()
    @classmethod
    def native(cls):
        return cls(Position.native())
    @property
    def termination(self):
        ans = self.position.termination
        if ans is not None:
            return ans
        if self.halfmove_clock >= 150:
            ans = Termination(
                kind=Termination.Kind.SEVENTYFIVE_MOVES,
                subject=self.position.turn.opponent(),
            )
        return ans

