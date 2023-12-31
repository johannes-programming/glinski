from __future__ import annotations

import typing
from dataclasses import dataclass

from glinski._enums.pieces import *
from glinski._enums.players import *

__all__ = ['Piece']

WHITE_SYMBOLS = {
    PieceType.PAWN:'P',
    PieceType.KNIGHT:'N',
    PieceType.BISHOP:'B',
    PieceType.ROOK:'R',
    PieceType.QUEEN:'Q',
    PieceType.KING:'K',
}

@dataclass(frozen=True)
class BasePiece:
    pieceType:PieceType
    player:Player
    @classmethod
    def from_symbol(cls, symbol: str) -> Piece:
        if type(symbol) is not str:
            raise TypeError(symbol)
        for pieceType, white_symbol in WHITE_SYMBOLS.items():
            if white_symbol != symbol.upper():
                continue
            return cls(
                pieceType=pieceType,
                player=Player(white_symbol == symbol),
            )
        raise ValueError(symbol)
    def invert(self) -> typing.Self:
        cls = type(self)
        ans = cls(
            pieceType=self.pieceType,
            player=self.player.invert(),
        )
        return ans
    def symbol(self) -> str:
        ans = WHITE_SYMBOLS[self.pieceType]
        if self.player == Player.BLACK:
            ans = ans.lower()
        return ans
    def unicode_symbol(self) -> str:
        code = 9824
        code -= int(self.player.value) * 6
        code -= self.pieceType.value
        ans = chr(code)
        return ans

class Piece(BasePiece):
    def __init__(self, *, 
        pieceType:PieceType, 
        player:Player,
    ):
        if type(pieceType) is not PieceType:
            raise TypeError(pieceType)
        if type(player) is not Player:
            raise TypeError(player)
        super().__init__(
            pieceType=pieceType,
            player=player,
        )
    
