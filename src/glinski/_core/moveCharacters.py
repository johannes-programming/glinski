import typing
from dataclasses import dataclass

from .pieces import *

__all__ = ['MoveCharacter']

@dataclass
class MoveCharacter:
    subject:typing.Optional[Piece] = None
    target:typing.Optional[Piece] = None
    ep:bool = False
    def is_capture(self) -> bool:
        if self.target is not None:
            return True
        if self.ep:
            return True
        return False


