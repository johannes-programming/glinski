from __future__ import annotations

import typing
from dataclasses import dataclass

from glinski._enums.pieces import *
from glinski._enums.players import *

__all__ = ['Piece']

WHITE_SYMBOLS = {
    PieceKind.PAWN:'P',
    PieceKind.KNIGHT:'N',
    PieceKind.BISHOP:'B',
    PieceKind.ROOK:'R',
    PieceKind.QUEEN:'Q',
    PieceKind.KING:'K',
}

@dataclass(frozen=True)
class BasePiece:
    kind:PieceKind
    player:Player
    @classmethod
    def from_symbol(cls, symbol: str) -> Piece:
        if type(symbol) is not str:
            raise TypeError(symbol)
        for kind, white_symbol in WHITE_SYMBOLS.items():
            if white_symbol != symbol.upper():
                continue
            return cls(
                kind=kind,
                player=Player(white_symbol == symbol),
            )
        raise ValueError(symbol)
    def invert(self) -> typing.Self:
        cls = type(self)
        ans = cls(
            kind=self.kind,
            player=self.player.invert(),
        )
        return ans
    def symbol(self) -> str:
        ans = WHITE_SYMBOLS[self.kind]
        if self.player == Player.BLACK:
            ans = ans.lower()
        return ans
    def unicode_symbol(self) -> str:
        code = 9824
        code -= int(self.player.value) * 6
        code -= self.kind.value
        ans = chr(code)
        return ans

class Piece(BasePiece):
    def __init__(self, *, 
        kind:PieceKind, 
        player:Player,
    ):
        if type(kind) is not PieceKind:
            raise TypeError(kind)
        if type(player) is not Player:
            raise TypeError(player)
        super().__init__(
            kind=kind,
            player=player,
        )
    
