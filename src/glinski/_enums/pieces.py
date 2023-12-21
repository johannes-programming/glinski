from __future__ import annotations

import enum as _enum
import typing as _typing

from .PlayerColor import PlayerColor

__all__ = [
    'PieceType',
    'PieceKind',
]

_BLACK_LETTERS = {
    1:'p',
    2:'n',
    3:'b',
    4:'r',
    5:'q',
    6:'k',
}

class PieceType(_enum.Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    def white(self) -> PieceKind:
        return self.pieceKind(
            playerColor=PlayerColor.WHITE,
        )
    def black(self) -> PieceKind:
        return self.pieceKind(
            playerColor=PlayerColor.BLACK,
        )
    def pieceKind(self, 
        playerColor:PlayerColor,
    ) -> PieceKind:
        s = _BLACK_LETTERS[self.value]
        if playerColor:
            s = s.upper()
        ans = PieceKind[s]
        return ans

class PieceKind(_enum.Enum):
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
    def invert(self) -> _typing.Self:
        if self.playerColor():
            return self.black()
        else:
            return self.white()
    def white(self) -> _typing.Self:
        return self.pieceType().white()
    def black(self) -> _typing.Self:
        return self.pieceType().black()
    def playerColor(self) -> _typing.Self:
        return PlayerColor(self.name < '_')
    def pieceType(self) -> PieceType:
        black_name = self.name.lower()
        for number, letter in _BLACK_LETTERS.items():
            if black_name == letter:
                return PieceType(number)
        raise NotImplementedError
    


