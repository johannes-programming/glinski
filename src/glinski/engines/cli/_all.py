import random

from glinski._core import *

__all__ = ['move']

def move(seq:Seq) -> Move:
    if type(seq) is not Seq:
        raise TypeError(seq)
    print(seq.end.board)
    print(f"ep_cell={seq.end.ep_cell}")
    while True:
        uci = input("Your legal move (uci)? ")
        ans = Move.by_uci(uci)
        if ans is None:
            break
        if seq.end.is_legal_move(ans):
            break
        print("Illegal.")
    return ans



