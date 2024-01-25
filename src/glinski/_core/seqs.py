# imports
import typing

from .errors import *
from .players import *
from .plies_and_positions import *
from .terminations import *

# __all__
__all__ = ['Seq']




# classes
class Seq:
    # dunder
    def __bool__(self):
        return bool(len(self))
    def __eq__(self, other) -> bool:
        cls = type(self)
        if type(other) is not cls:
            return False
        return self._plies == other._plies
    def __getitem__(self, key):
        cls = type(self)
        if type(key) is int:
            return self._plies[key]
        if type(key) is not slice:
            raise TypeError(key)
        if key.step not in {None, 1}:
            raise ValueError(key)
        if key.start is None:
            start = 0
        else:
            start = key.start
        if start < len(self):
            root = self._plies[start]
        else:
            root = Position()
        plies = self._plies[key]
        ucis = [ply.uci for ply in plies]
        ans = cls(*ucis, root=root)
        return ans
    def __hash__(self) -> int:
        return self._plies.__hash__()
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, 
        root:Position,
        *ucis:Ply.UCI,
    ) -> None:
        ...
    def __init__(self, 
        root:Position=None,
        *ucis:Ply.UCI,
    ) -> None:
        plies = list()
        self._terminations = list()
        before = root
        ucis = tuple(ucis)
        for uci in ucis:
            t = self.__termination(before)
            self._terminations.append(t)
            ply = Ply(before=before, uci=uci)
            plies.append(ply)
            before = ply.after
        self._plies = tuple(plies)
        self._is_legal = root.is_legal
        for ply in self._plies:
            self._is_legal &= ply.is_legal
        for t in self._terminations:
            self._is_legal &= t is None
        t = self.__termination(before)
        self._terminations.append(t)
    def __iter__(self):
        return iter(self._plies)
    def __len__(self):
        return len(self._plies)
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    

    #
    @classmethod
    def __termination(self, position):
        ans = position.termination
        if ans is not None:
            return ans
        count = 1 + sum(
            position.is_repetition(ply.before)
            for ply in self._plies
        )
        if 5 <= count:
            ans = Termination(
                kind=Termination.Kind.FIVEFOLD_REPETITION,
                subject=position.turn.turntable(),
            )
        return ans
    

    
    # others
    def apply(self, *ucis:Ply.UCI):
        cls = type(self)
        ucis = self.ucis + tuple(ucis)
        ans = cls(
            root=self.root,
            ucis=ucis,
        )
        return ans
    @property
    def is_legal(self):
        return self._is_legal
    def termination(self, index, /):
        return self._terminations[index]





