import random

from glinski._core import *

__all__ = ['move']

def move(seq:Seq) -> Move:
    if type(seq) is not Seq:
        raise TypeError(seq)
    return random.choice(list(seq.end.legal_moves()))



