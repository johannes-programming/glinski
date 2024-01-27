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
    def _init_null(self) -> None:
        self._init(root=Position())
    @typing.overload
    def __init__(self, 
        *ucis:Ply.UCI,
        root:Position,
    ) -> None:
        ...
    def _init_not_null(self, 
        *ucis:Ply.UCI,
        root:Position,
    ) -> None:
        self._init(*ucis, root=root)
    def __init__(self, *args, **kwargs) -> None:
        if len(args) + len(kwargs):
            self._init_not_null(*args, **kwargs)
        else:
            self._init_null()
    def _init(self, 
        *ucis:Ply.UCI,
        root:Position,
    ) -> None:
        root = Position(root)
        before = root
        plies = list()
        terminations = list()
        ucis = tuple(ucis)
        for uci in ucis:
            t = self._termination(before)
            terminations.append(t)
            ply = Ply(before=before, uci=uci)
            plies.append(ply)
            before = ply.after()
        self._plies = tuple(plies)
        self._is_legal = root.is_legal()
        for ply in self._plies:
            self._is_legal &= ply.is_legal()
        for t in terminations:
            self._is_legal &= t is None
        t = self._termination(before)
        terminations.append(t)
        self._terminations = tuple(terminations)
    def __iter__(self):
        return iter(self._plies)
    def __len__(self):
        return len(self._plies)
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    

    #
    @classmethod
    def _termination(self, position):
        ans = position.termination()
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





