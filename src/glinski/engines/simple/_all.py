import random

from glinski._core import *

__all__ = ['move']

OUTCOME_VALUES = {
    Outcome.FULL_WIN_FOR_WHITE:1e6,
    Outcome.HALF_WIN_FOR_WHITE:0,
    Outcome.DRAW:0,
    Outcome.HALF_WIN_FOR_BLACK:0,
    Outcome.FULL_WIN_FOR_BLACK:-1e6,
}

def move(seq:Seq) -> Move:
    if type(seq) is not Seq:
        raise TypeError(seq)
    path, value = recursion(seq, -2)
    return path[0]

def recursion(
        seq:Seq, 
        depth:int, 
):
    if type(seq) is not Seq:
        raise TypeError(seq)
    depth = int(depth)
    if seq.termination is not None:
        value = OUTCOME_VALUES[seq.termination.outcome]
        return [], value
    if depth >= 0:
        return [], eva(seq)
    legal_moves = list(seq.end.legal_moves())
    deeper_values = list()
    paths = list()
    for legal_move in legal_moves:
        deeper_seq = seq.apply(legal_move)
        deeper_depth = depth + 1
        path, deeper_value = recursion(
            seq=deeper_seq, 
            depth=deeper_depth,
        )
        deeper_values.append(deeper_value)
        paths.append(path)
    if seq.end.turn == Player.WHITE:
        extreme = max(deeper_values)
    else: 
        extreme = min(deeper_values)
    index = deeper_values.index(extreme)
    legal_move = legal_moves[index]
    path = [legal_move] + paths[index]
    return path, extreme


    





def eva(seq:Seq):
    if type(seq) is not Seq:
        raise TypeError(seq)
    termination = seq.termination
    if termination is not None:
        white = termination.outcome.value[0]
        if white == 1.0:
            return 1e6
        if white == 0.0:
            return -1e6
        return 0
    ans = 0
    for cell in Cell:
        piece = seq.end.board.piece(cell)
        if piece is None:
            continue
        kind = piece.kind
        value = [1, 3, 3, 5, 9, 0][kind]
        if piece.player == Player.BLACK:
            value *= -1
        ans += value
    return ans


