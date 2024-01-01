from __future__ import annotations

import typing
from dataclasses import dataclass
from enum import Enum

from .players import Player

__all__ = ['Piece']


@dataclass(frozen=True)
class BasePiece:
    kind:Piece.Kind
    player:Player
    def invert(self) -> typing.Self:
        cls = type(self)
        ans = cls(
            kind=self.kind,
            player=self.player.invert(),
        )
        return ans
    def symbol(self) -> str:
        ans = self.kind.value
        if ans == '':
            ans = 'P'
        if self.player == Player.BLACK:
            ans = ans.lower()
        return ans
    @classmethod
    def by_symbol(cls, value: str) -> Piece:
        if type(value) is not str:
            raise TypeError(value)
        for player in Player:
            for kind in Piece.Kind:
                ans = cls(player=player, kind=kind)
                if ans.symbol() == value:
                    return ans
        raise ValueError(value)
    
    def unicode_symbol(self) -> str:
        code = 9824
        code -= int(self.player.value) * 6
        code -= self.kind.value
        ans = chr(code)
        return ans
    @classmethod
    def by_unicode_symbol(cls, value:str) -> typing.Self:
        if type(value) is not str:
            raise TypeError(value)
        for player in Player:
            for kind in Piece.Kind:
                ans = cls(player=player, kind=kind)
                if ans.unicode_symbol() == value:
                    return ans
        raise ValueError(value)

class Piece(BasePiece):
    class Kind(Enum):
        PAWN = ''
        KNIGHT = 'N'
        BISHOP = 'B'
        ROOK = 'R'
        QUEEN = 'Q'
        KING = 'K'
        def algebraic(self):
            return self.value
        @classmethod
        def by_algebraic(cls, value):
            return cls[value]
        def uci(self) -> typing.Optional[str]:
            if self.value in {'', 'K'}:
                return None
            else:
                return self.value.lower()
        @classmethod
        def by_uci(cls, value:str, /) -> typing.Self:
            if type(value) is not str:
                raise TypeError(value)
            for k in cls:
                if value == k.uci():
                    return k
            raise ValueError(value)
        def promotion(self) -> bool:
            return self.uci() is not None
        @classmethod
        def promotions(cls) -> typing.Set[typing.Self]:
            return {x for x in cls if x.promotion()}

    def __init__(self, *, 
        kind:Piece.Kind, 
        player:Player,
    ):
        if type(kind) is not Piece.Kind:
            raise TypeError(kind)
        if type(player) is not Player:
            raise TypeError(player)
        super().__init__(
            kind=kind,
            player=player,
        )




