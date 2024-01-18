# imports
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .outcomes import *
from .players import *

# __all__
__all__ = ['Termination']




# classes
@dataclass(frozen=True)
class BaseTermination:
    kind:Termination.Kind
    subject:Player
    outcome:Outcome
class Termination(BaseTermination):
    class Kind(Enum):
        CHECKMATE = 1
        STALEMATE = 2
        SEVENTYFIVE_MOVES = 4
        FIVEFOLD_REPETITION = 5
        def for_subject(self) -> float:
            cls = type(self)
            ans = {
                cls.CHECKMATE:1.00,
                cls.STALEMATE:0.75,
                cls.SEVENTYFIVE_MOVES:0.50,
                cls.FIVEFOLD_REPETITION:0.50,
            }[self]
            return ans
        def for_opponent(self) -> float:
            x = self.for_subject()
            if x is None:
                return None
            return 1.0 - x
    def __init__(self, *, 
        kind:Termination.Kind,
        subject:Player,
    ):
        if type(kind) is not Termination.Kind:
            raise TypeError(kind)
        if type(subject) is not Player:
            raise TypeError(subject)
        if subject == Player.WHITE:
            white = kind.for_subject()
        else:
            white = kind.for_opponent()
        outcome = Outcome.by_items(white=white)
        super().__init__(
            kind=kind,
            outcome=outcome,
            subject=subject,
        )
        
        

