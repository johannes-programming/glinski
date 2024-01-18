# imports
from __future__ import annotations

import typing
from enum import IntEnum

from .players import *

# __all__
__all__ = ['Piece']




# classes
class Kind(IntEnum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

    # algebraic
    @property
    def algebraic(self):
        cls = type(self)
        ans = {
            cls.PAWN:'',
            cls.KNIGHT:'N',
            cls.BISHOP:'B',
            cls.ROOK:'R',
            cls.QUEEN:'Q',
            cls.KING:'K',
        }[self]
        return ans
    @classmethod
    def by_algebraic(cls, value, /):
        for x in cls:
            if x.algebraic == value:
                return x
        raise ValueError(value)
    
    # uci
    @property
    def uci(self) -> typing.Optional[str]:
        ans = self.algebraic.lower()
        if ans in {'', 'k'}:
            ans = None
        return ans
    @classmethod
    def by_uci(cls, value:str, /) -> typing.Self:
        v = str(value)
        for k in cls:
            if v == k.uci:
                return k
        raise ValueError(value)

    # properties
    @property
    def sliding(self) -> bool:
        return 2 <= self <= 4
    




class Piece(IntEnum):

    # fields
    P = 0
    N = 1
    B = 2
    R = 3
    Q = 4
    K = 5
    p = 6
    n = 7
    b = 8
    r = 9
    q = 10
    k = 11
    
    # properties
    @property
    def kind(self) -> Piece.Kind:
        return Piece.Kind(self % 6)
    @property
    def player(self) -> Player:
        return Player(self // 6)
    @classmethod
    def by_kind_and_player(cls, 
        kind:Piece.Kind,
        player:Player,
    ) -> typing.Self:
        kind = Piece.Kind(kind)
        player = Player(player)
        value = player * 6 + kind
        ans = cls(value)
        return ans
    
    #   fen
    @property
    def fen(self) -> str:
        return self.name
    @classmethod
    def by_fen(cls, value: str) -> Piece:
        return cls[value]
    #   unicode
    @property
    def unicode(self) -> str:
        return chr(9823 - self)
    @classmethod
    def by_unicode(cls, value:str) -> typing.Self:
        if type(value) is not str:
            raise TypeError(value)
        for player in Player:
            for kind in Piece.Kind:
                ans = cls(player=player, kind=kind)
                if ans.unicode() == value:
                    return ans
        raise ValueError(value)

    # methods
    def swapplayer(self) -> typing.Self:
        cls = type(self)
        ans = cls.by_kind_and_player(
            kind=self.kind,
            player=self.player.opponent(), 
        )
        return ans
    
Piece.Kind = Kind



