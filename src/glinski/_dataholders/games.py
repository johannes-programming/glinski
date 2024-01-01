import typing

from glinski._dataholders.moves import *
from glinski._dataholders.positions import *
from glinski._dataholders.terminations import *
from glinski._enums import *
from glinski._errors import *

__all__ = ['Game']

NATIVE_POSITION = Position.native()

class Game:

    # methods
    #   dunder
    def __init__(self, root:Position=NATIVE_POSITION) -> None:
        if type(root) is not Position:
            raise TypeError(root)
        if not root.is_legal():
            raise ValueError(root)
        self._moves = list()
        self._positions = [root]
        self._offers = dict()
    def __len__(self):
        return len(self._moves)
        
    #   protected
    def _assume_no_termation(self):
        if self.termination() is not None:
            raise GameAlreadyOverError
    def _is_zeroing(self, index):
        return self.positions()[index].is_zeroing(self.moves()[index])
    def _terminate(self, *args, **kwargs):
        self._assume_no_termation()
        self._termination = Termination(
            *args,
            **kwargs,
        )
        self._offers = dict()
    def _terminate_by_boredom(self):
        if self.repetition() >= 5:
            self._terminate(
                kind=TerminationKind.FIVEFOLD_REPETITION,
                subject=self.turn().invert(),
            )
        elif self.halfmove_clock() >= 150:
            self._terminate(
                kind=TerminationKind.SEVENTYFIVE_MOVES,
                subject=self.turn().invert(),
            )
        else:
            return True
        return False
    def _terminate_by_position(self):
        t = self.position().termination()
        if t is None:
            return False
        self._terminate(
            kind=t.kind,
            subject=t.subject,
            outcome=t.outcome,
        )
        return True
    def _terminate_by_stack(self):
        if self._terminate_by_position():
            return True
        if self._terminate_by_boredom():
            return True
        return False


    #   public

    def append(self, move:Move) -> None:
        self._assume_no_termation()
        before = self.position()
        afterwards = before.apply(move)
        if afterwards.is_anticheck():
            raise AnticheckError(move)
        self._offers.pop(afterwards.turn, None)
        self._moves.append(move)
        self._positions.append(afterwards)
        self._terminate_by_stack()
    
    def copy(self) -> typing.Self:
        cls = type(self)
        ans = cls(self.root())
        for m in self.moves():
            ans.append(m)
        ans._offers = dict(self._offers)
        return ans

    def current_offer_by(self, player:Player):
        if type(player) is not Player:
            raise TypeError(player)
        return self._current_offer_by.get(player)
    
    def extend(self, moves:typing.Iterable[Move]) -> None:
        for move in moves:
            self.append(move)

    def halfmove_clock(self) -> int:
        l = len(self)
        for j in range(l):
            i = l - j - 1
            if self._is_zeroing(i):
                return j
        return l

    def moves(self) -> typing.Tuple[Move]:
        return tuple(self._moves)
    
    def pop(self) -> Move:
        ans, = self.rewind(1)
        return ans
    
    def position(self) -> Position:
        return self.positions()[-1]

    def positions(self) -> typing.Tuple[Position]:
        return tuple(self._positions)
    
    def repetition(self) -> int:
        lastpositions = self.positions()[-self.halfmove_clock():]
        ans = 0
        for p in lastpositions:
            if p == self.positions()[-1]:
                ans += 1
        return ans
    
    def rewind(self, count:int) -> typing.List[Move]:
        if type(count) is not int:
            raise TypeError(count)
        if not (0 <= count <= len(self)):
            raise IndexError(count)
        ans = self.moves()[-count:]
        self._offers = dict()
        self._moves = self.moves()[:-count]
        self._positions = self.positions()[:-count]
        self._termination = None
        self._terminate_by_stack()
        return ans
    
    def root(self):
        return self.positions()[0]
    
    def termination(self):
        return self._termination
    
    def turn(self):
        return self.position().turn()





