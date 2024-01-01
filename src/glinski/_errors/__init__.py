class ChessError(ValueError):
    pass
class MoveError(ChessError):
    pass
class UnsoundMoveError(MoveError):
    pass
class AnticheckError(MoveError):
    pass
class GameAlreadyOverError(ChessError):
    pass