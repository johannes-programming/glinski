from __future__ import annotations

import typing
from enum import Enum

from .players import *

__all__ = [
    'PieceType',
    'PieceKind',
]

BLACKLETTERS = {
    1:'p',
    2:'n',
    3:'b',
    4:'r',
    5:'q',
    6:'k',
}

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    def black(self) -> PieceKind:
        return self.pieceKind(Player.BLACK)
    def pieceKind(self, player:Player) -> PieceKind:
        s = BLACKLETTERS[self.value]
        if player.value:
            s = s.upper()
        ans = PieceKind[s]
        return ans
    def promotion(self) -> bool:
        return self in self.promotions()
    @classmethod
    def promotions(cls) -> typing.Set[typing.Self]:
        return {
            cls.KNIGHT,
            cls.BISHOP,
            cls.ROOK,
            cls.QUEEN,
        }
    def white(self) -> PieceKind:
        return self.pieceKind(Player.WHITE)

class PieceKind(Enum):
    P = "♙"
    p = "♟"
    N = "♘"
    n = "♞"
    B = "♗"
    b = "♝"
    R = "♖"
    r = "♜"
    Q = "♕"
    q = "♛"
    K = "♔"
    k = "♚"
    def black(self) -> typing.Self:
        return self.pieceType().black()
    def invert(self) -> typing.Self:
        if self.player().value:
            return self.black()
        else:
            return self.white()
    def pieceType(self) -> PieceType:
        black_name = self.name.lower()
        for number, letter in BLACKLETTERS.items():
            if black_name == letter:
                return PieceType(number)
        raise NotImplementedError
    def player(self) -> typing.Self:
        return Player(self.name < '_')
    def white(self) -> typing.Self:
        return self.pieceType().white()
    


