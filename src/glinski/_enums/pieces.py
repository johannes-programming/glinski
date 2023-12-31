from __future__ import annotations

import typing
from enum import Enum

from .players import *

__all__ = ['PieceType']



NOTATIONS = None
PROMOTIONS = None

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    @classmethod
    def by_notation(cls, value, /) -> typing.Self:
        value = str(value)
        for k, v in NOTATIONS.items():
            if v == value:
                return k
        raise ValueError(value)
    def notation(self) -> str:
        return NOTATIONS[self]
    def promotion(self) -> bool:
        return self in PROMOTIONS
    @classmethod
    def promotions(cls) -> typing.Set[typing.Self]:
        return PROMOTIONS

NOTATIONS = {
    PieceType.PAWN:"",
    PieceType.KNIGHT:"N",
    PieceType.BISHOP:"B",
    PieceType.ROOK:"R",
    PieceType.QUEEN:"Q",
    PieceType.KING:"K",
}
PROMOTIONS = {
    PieceType.KNIGHT,
    PieceType.BISHOP,
    PieceType.ROOK,
    PieceType.QUEEN,
}


