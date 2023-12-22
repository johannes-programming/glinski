import typing as _typing

import isometric as _iso

from glinski import _vectors
from glinski._enums import *

__all__ = ['Board']
ATTRS = [
    'clear',
    'get',
    'pop',
    'popitem',
]



class Board:
    @property
    def data(self):
        return self._data
    def __init__(self, data={}) -> None:
        self._data = dict()
        self.update(data)
    def __getitem__(self, key):
        return self._data[key]
    def __setitem__(self, key, value):
        if type(key) is not Cell:
            raise TypeError
        if type(value) is not PieceKind:
            raise TypeError
        self._data[key] = value
    def __delitem__(self, key):
        del self._data[key]
    def __getattr__(self, attr):
        if attr in ATTRS:
            return getattr(self._data, attr)
        raise AttributeError(attr)
    def __str__(self) -> str:
        return self.text()
    def text(self, *, hpad=3, vpad=0, unicode=False):
        empty = [" "] * 11
        hspacer = " " * hpad
        emptyline = hspacer.join(hspacer)
        vspacer = emptyline.join(['\n'] * (vpad + 1))
        table = [list(empty) for i in range(21)]
        for cell in Cell:
            desc = cell.value.description()
            i = 5 + desc.y
            j = 10 + desc.y - desc.z - desc.z
            pieceKind = self.get(cell)
            if pieceKind is None:
                s = '.'
            elif unicode:
                s = pieceKind.value
            else:
                s = pieceKind.name
            table[j][i] = s
        lines = [hspacer.join(row) for row in table]
        ans = vspacer.join(lines)
        return ans
    def copy(self):
        cls = type(self)
        ans = cls(self._data)
        return ans
    @classmethod
    def fromkeys(cls, iterable, value=None, /):
        ans = cls()
        for k in iterable:
            ans[k] = value
        return ans
    def items(self):
        return tuple(self._data.items())
    def keys(self):
        return tuple(self._data.keys())
    def setdefault(self, key, default, /):
        if key in self._data.keys():
            return
        self[key] = default
    def update(self, obj, /):
        cls = type(self)
        if type(obj) is cls:
            obj = obj.data
        obj = dict(obj)
        for k, v in obj.items():
            self[k] = v
    def values(self):
        return tuple(self._data.values())
    
    def invert(self):
        cls = type(self)
        ans = cls()
        for k, v in self._data.items():
            ans[k.vflip()] = v.invert()
        return ans
    @classmethod
    def native(cls):
        ans = cls()
        ans.reset()
        return ans
    def reset(self):
        for cell in Cell:
            pieceKind = cell.native()
            if pieceKind is None:
                self.pop(cell, None)
            else:
                self[cell] = pieceKind
    def check(self, currentPlayer:PlayerColor):
        currentKing = PieceType.KING.pieceKind(currentPlayer)
        for cell, pieceKind in self._data.items():
            if currentKing != pieceKind:
                continue
            if self._check(cell):
                return True
        return False
    def _check(self, cell):
        currentKing = self[cell]
        currentPlayer = currentKing.playerColor()
        
        if currentPlayer == PlayerColor.WHITE:
            pawnVector = _vectors.BLACKPAWN
        else:
            pawnVector = _vectors.WHITEPAWN

        # pawns
        if self._check_directions(
            cell=cell,
            rotate=False,
            hflip=True,
            vector=pawnVector,
            pieceTypes=[PieceType.PAWN],
            scale=False,
        ):
            return True
        # knights
        if self._check_directions(
            cell=cell,
            rotate=True,
            hflip=True,
            vector=_vectors.KNIGHT,
            pieceTypes=[PieceType.KNIGHT],
            scale=False,
        ):
            return True
        # unscaled file
        if self._check_directions(
            cell=cell,
            rotate=True,
            hflip=False,
            vector=_vectors.FILE,
            pieceTypes=[PieceType.ROOK, PieceType.QUEEN, PieceType.KING],
            scale=False,
        ):
            return True
        # scaled file
        if self._check_directions(
            cell=cell,
            rotate=True,
            hflip=False,
            vector=_vectors.FILE,
            pieceTypes=[PieceType.ROOK, PieceType.QUEEN],
            scale=True,
        ):
            return True
        # unscaled diagonal
        if self._check_directions(
            cell=cell,
            rotate=True,
            hflip=False,
            vector=_vectors.DIAGONAL,
            pieceTypes=[PieceType.BISHOP, PieceType.QUEEN, PieceType.KING],
            scale=False,
        ):
            return True
        # scaled diagonal
        if self._check_directions(
            cell=cell,
            rotate=True,
            hflip=False,
            vector=_vectors.DIAGONAL,
            pieceTypes=[PieceType.BISHOP, PieceType.QUEEN],
            scale=True,
        ):
            return True
        return False
    


    def _check_directions(self, *, 
        cell:Cell,
        rotate:bool,
        hflip:bool,
        vector:_iso.Vector,
        pieceTypes:_typing.List[PieceType],
        scale:bool,
    ):
        currentPlayer = self[cell].playerColor()
        vectors = [vector]
        if hflip:
            vectors.append(vector.hflip())
        if scale:
            factors = range(2, 100)
        else:
            factors = [1]
        if rotate:
            stepss = range(6)
        else:
            stepss = [0]
        for steps in stepss:
            for v in vectors:
                for n in factors:
                    w = cell.value - (v * n).rotate(steps)
                    try:
                        checker = Cell(w)
                    except ValueError as exc:
                        break # over the edge
                    if checker not in self._data.keys():
                        continue # empty cell
                    pieceKind = self[checker]
                    if pieceKind.playerColor() == currentPlayer:
                        break # same playerColor
                    if pieceKind.pieceType() not in pieceTypes:
                        break # not pieceType of interest
                    return True # found source of check
        return False
