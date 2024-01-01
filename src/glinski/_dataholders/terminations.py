from dataclasses import dataclass

from glinski._enums import *

__all__ = ['Termination']

@dataclass(frozen=True)
class BaseTermination:
    kind:TerminationKind
    subject:Player
    outcome:Outcome

class Termination(BaseTermination):
    def __init__(self, *, 
        kind:TerminationKind,
        subject:Player,
    ):
        if type(kind) is not TerminationKind:
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
        
        

