

class MoveError(ValueError):
    pass
class IllegalMoveError(MoveError):
    pass
class UnsoundMoveError(IllegalMoveError):
    pass

