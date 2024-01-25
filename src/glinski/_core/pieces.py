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

    #
    @classmethod
    def _setup(cls):
        #
        cls.PAWN._ALGEBRAIC = ''
        cls.KNIGHT._ALGEBRAIC = 'N'
        cls.BISHOP._ALGEBRAIC = 'B'
        cls.ROOK._ALGEBRAIC = 'R'
        cls.QUEEN._ALGEBRAIC = 'Q'
        cls.KING._ALGEBRAIC = 'K'
        #
        cls.PAWN._UCI = None
        cls.KNIGHT._UCI = 'n'
        cls.BISHOP._UCI = 'b'
        cls.ROOK._UCI = 'r'
        cls.QUEEN._UCI = 'q'
        cls.KING._UCI = None

    # conversion
    @property
    def algebraic(self):
        return self._ALGEBRAIC
    @classmethod
    def by_algebraic(cls, value, /):
        for x in cls:
            if x.algebraic == value:
                return x
        raise ValueError(value)
    @property
    def uci(self) -> str:
        ans = self._UCI
        if ans is None:
            raise ValueError(self)
        else:
            return ans
    @classmethod
    def by_uci(cls, value:str, /, allow_empty=False) -> typing.Self:
        v = str(value)
        if allow_empty and (v == ""):
            return None
        for x in cls:
            if x.uci == v:
                return x
        raise ValueError(value)

    # properties
    @property
    def is_sliding(self) -> bool:
        return 2 <= self <= 4
    




class Piece(IntEnum):
    # fields
    (
        P, N, B, R, Q, K, 
        p, n, b, r, q, k,
    ) = range(12)

    # protected
    @classmethod
    def _setup(cls):
        pass
    
    # conversion
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
    @property
    def fen(self) -> str:
        return self.name
    @classmethod
    def by_fen(cls, value: str) -> Piece:
        return cls[value]
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
    def turntable(self) -> typing.Self:
        cls = type(self)
        ans = cls.by_kind_and_player(
            kind=self.kind,
            player=self.player.turntable(), 
        )
        return ans
    
Piece.Kind = Kind



