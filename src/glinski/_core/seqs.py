import typing
from dataclasses import dataclass

from .errors import *
from .moves import *
from .players import *
from .positions import *
from .terminations import *

__all__ = ['Seq']

NATIVE_POSITION = Position.native()

@dataclass(frozen=True)
class BaseSeq:
    _positions:typing.Tuple[Position]
    moves:typing.Tuple[Move]
    repetition:int
    reversible:int
    termination:Termination






class Seq(BaseSeq):
    # methods
    #   dunder
    def __init__(self, *,
        root:Position=NATIVE_POSITION,
        moves:typing.Iterable[Move]=[],
    ) -> None:
        if type(root) is not Position:
            raise TypeError(root)
        if not root.is_legal():
            raise NotLegalError(root)
        moves = list(moves)
        positions = [root]
        repetition = 1
        reversible = 0
        termation = self._termination(
            end=positions[-1],
            repetition=repetition,
            reversible=reversible,
        )
        for move in moves:
            if termation is not None:
                raise NotLegalError(termation)
            positions.append(positions[-1].apply(move))
            if positions[-1].is_illegal_check():
                raise NotLegalError(move)
            repetition = positions.count(positions[-1])
            if positions[-2].is_reversible(move):
                reversible += 1
            else:
                reversible = 0
            termation = self._termination(
                end=positions[-1],
                repetition=repetition,
                reversible=reversible,
            )
        super().__init__(
            _positions=tuple(positions),
            moves=tuple(moves),
            repetition=repetition,
            reversible=reversible,
            termination=termation,
        )
    

    #   protected
    @classmethod
    def _termination(cls, *, 
        end,
        repetition,
        reversible,
    ) -> typing.Optional[Termination]:
        end_termination = end.termination()
        if end_termination is not None:
            return end_termination
        if repetition >= 5:
            return Termination(
                kind=Termination.Kind.FIVEFOLD_REPETITION,
                subject=end.turn.invert(),
            )
        if reversible >= 150:
            return Termination(
                kind=Termination.Kind.SEVENTYFIVE_MOVES,
                subject=end.turn.invert(),
            )
        return None


    #   public
    #     positions
    @property
    def after(self):
        return self._positions[1:]
    @property
    def before(self):
        return self._positions[:-1]
    @property
    def end(self):
        return self._positions[-1]
    @property
    def root(self):
        return self._positions[0]
    


    #     others
    def apply(self, *moves):
        cls = type(self)
        moves = self.moves + tuple(moves)
        ans = cls(
            moves=moves,
            root=self.root,
        )
        return ans
    def flatten(self, index:typing.Optional[int]=-1, /):
        cls = type(self)
        if index is None:
            root = self.end
            moves = []
        else:
            if index < 0:
                index += len(self._positions)
            root = self._positions[index]
            moves = self.moves[index:]
        ans = cls(
            root=root,
            moves=moves,
        )
        return ans
    def reset(self, index:typing.Optional[int]=None) -> typing.Self:
        cls = type(self)
        if index is None:
            moves = []
        else:
            moves = self.moves[:index]
        ans = cls(
            root=self.root,
            moves=moves,
        )
        return ans





