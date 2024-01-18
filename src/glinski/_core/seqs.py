# imports
import typing
from dataclasses import dataclass

from .errors import *
from .fenPositions import *
from .players import *
from .plies import *
from .terminations import *

# __all__
__all__ = ['Seq']




# classes
@dataclass(frozen=True)
class BaseSeq:
    _fenPositions:typing.Tuple[FENPosition]
    plies:typing.Tuple[Move]
class Seq(BaseSeq):
    # dunder
    def __init__(self, *,
        plies:typing.Iterable[Move]=[],
        root:FENPosition=FENPosition(),
    ) -> None:
        if type(root) is not FENPosition:
            raise TypeError(root)
        _fenPositions = [root]
        plies = tuple(plies)
        for ply in plies:
            before = _fenPositions[-1]
            after = before.apply(ply)
            _fenPositions.append(after)
        super().__init__(
            _fenPositions=_fenPositions,
            plies=plies,
        )
    # positions
    @property
    def after(self):
        return self._fenPositions[1:]
    @property
    def before(self):
        return self._fenPositions[:-1]
    @property
    def end(self):
        return self._fenPositions[-1]
    @property
    def root(self):
        return self._fenPositions[0]
    # others
    def apply(self, *plies):
        cls = type(self)
        plies = self.plies + tuple(plies)
        ans = cls(
            plies=plies,
            root=self.root,
        )
        return ans
    def flatten(self, index:int=-1, /):
        cls = type(self)
        if index >= 0:
            j = index
        else:
            j = index + 1
        plies = self.plies[j:]
        root = self._fenPositions[index]
        ans = cls(
            plies=plies,
            root=root,
        )
        return ans
    def is_legal(self):
        for fenPosition in self.before:
            if fenPosition.termination is not None:
                return False
        
    def reset(self, index:int=0) -> typing.Self:
        cls = type(self)
        if index >= 0:
            j = index
        else:
            j = index + 1
        plies = self.plies[j:]
        ans = cls(
            root=self.root,
            plies=plies,
        )
        return ans
    @property
    def termination(self):
        ans = self.end.termination
        if ans is not None:
            return ans
        i = -self.halfmove_clock - 1
        if self._fenPositions[i:].count(self.end) + 1 >= 5:
            ans = Termination(
                kind=Termination.Kind.FIVEFOLD_REPETITION,
                subject=self.end.position.turn.opponent(),
            )
        return ans





