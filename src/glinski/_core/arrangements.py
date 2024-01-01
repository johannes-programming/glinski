import typing
from dataclasses import dataclass

from .cells import *
from .consts import *
from .pieces import *
from .players import *

# __all__
__all__ = ['Arrangement']


# global constants
CELLS = tuple(Cell)
OPTIONAL_PIECES = typing.Optional[Piece]

# Arrangement
@dataclass(frozen=True)
class BaseArrangement:
    # fields
    _data:typing.Tuple[Piece]

    # methods
    #   dunder
    def __getitem__(self, key:Cell) -> OPTIONAL_PIECES:
        if type(key) is not Cell:
            raise TypeError(key)
        i = CELLS.index(key)
        ans = self._data[i]
        return ans
    
    #   protected
    @classmethod
    def _text(cls, 
        piece:OPTIONAL_PIECES, /, *, 
        unicode:bool,
    ) -> str:
        if piece is None:
            return '.'
        if unicode:
            return piece.unicode_symbol()
        else:
            return piece.symbol()
    
    def _zip(self) -> typing.Iterable[typing.Tuple[Cell, OPTIONAL_PIECES]]:
        return zip(CELLS, self._data)
    

    #   public
    def apply(self, 
        dictionary:typing.Dict[Cell, OPTIONAL_PIECES]={},
    ) -> typing.Self:
        cls = type(self)
        info = self.to_dict()
        info.update(dictionary)
        ans = cls(info)
        return ans
    
    def attackers(self, 
        cell:Cell, *,
        player:typing.Optional[Player]=None,
    ):
        if type(cell) is not Cell:
            raise TypeError(cell)
        if player is None:
            player = self[cell].player.invert()
        if type(player) is not Player:
            raise TypeError(player)

        ans = set()
        for finder in consts.attackerFinders.finders(player):
            for direction in finder.directions(cell):
                for c, pTs in direction:
                    p = self[c]
                    if p is None:
                        continue
                    if p.player == player:
                        if p.kind in pTs:
                            ans.add(c)
                    break
        return ans
    
    def attacks(self,
        cell:Cell, *,
        piece:typing.Optional[Piece]=None,
    ) -> typing.Optional[typing.Set[Cell]]:
        if type(cell) is not Cell:
            raise TypeError(cell)
        if piece is None:
            piece = self[cell]
        if piece is None:
            return set()
        if type(piece) is not Piece:
            raise TypeError(piece)
        ans = set()
        finder = consts.attackFinders.finder(piece)
        for direction in finder.directions(cell):
            for c in direction:
                p = self[c]
                if p is None:
                    ans.add(c)
                    continue
                if p.player != piece.player:
                    ans.add(c)
                break
        return ans
    
    def checkers(self, player:Player) -> typing.Set[Cell]:
        ans = set()
        for c, p in self._zip():
            if p is None:
                continue
            if p.player == player:
                continue
            if p.kind != Piece.Kind.KING:
                continue
            ans |= self.attackers(
                c,
                player=player,
            )
        return ans

    def invert(self) -> typing.Self:
        cls = type(self)
        dictionary = dict()
        for k, v in self._zip():
            if v is not None:
                dictionary[k.vflip()] = v.invert()
        ans = cls(dictionary)
        return ans
    
    def is_check(self, turn:Player) -> bool:
        return bool(len(self.checkers(turn.invert())))
    
    def items(self,
    ) -> typing.List[typing.Tuple[Cell, OPTIONAL_PIECES]]:
        return list(self._zip())
    
    @classmethod
    def keys(self) -> typing.List[Cell]:
        return list(CELLS)

    @classmethod
    def native(cls) -> typing.Self:
        dictionary = dict()
        for cell in Cell:
            dictionary[cell] = cell.native()
        ans = cls(dictionary)
        return ans

    def text(self, *, hpad=3, vpad=0, unicode=False) -> str:
        empty = [" "] * 11
        hspacer = " " * hpad
        emptyline = hspacer.join(hspacer)
        vspacer = emptyline.join(['\n'] * (vpad + 1))
        table = [list(empty) for i in range(21)]
        for cell in Cell:
            desc = cell.value.description()
            i = 5 + desc.y
            j = 10 + desc.y - desc.z - desc.z
            v = self[cell]
            s = self._text(v, unicode=unicode)
            table[j][i] = s
        lines = [hspacer.join(row) for row in table]
        ans = vspacer.join(lines)
        return ans
    
    def to_dict(self) -> typing.Dict[str, OPTIONAL_PIECES]:
        return dict(self._zip())
    
    def values(self) -> typing.List[OPTIONAL_PIECES]:
        return list(self._data)
    
    def where(self, *pieces:OPTIONAL_PIECES) -> typing.Set[Cell]:
        ans = set()
        for c, v in self._zip():
            if v in pieces:
                ans.add(c)
        return ans



class Arrangement(BaseArrangement):
    def __init__(self, 
        dictionary:typing.Dict[Cell, OPTIONAL_PIECES]={},
    ) -> None:
        data = [None] * len(CELLS)
        for k, v in dictionary.items():
            i = CELLS.index(k)
            if v is not None:
                if type(v) is not Piece:
                    raise TypeError(v)
            data[i] = v
        super().__init__(
            _data=tuple(data),
        )
    def __repr__(self) -> str:
        return str(self)
    def __str__(self) -> str:
        return self.text()



