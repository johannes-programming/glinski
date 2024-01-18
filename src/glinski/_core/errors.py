# classes
class ChessError(Exception):
    pass
class NotPseudolegalError(ChessError):
    pass
class NotLegalError(ChessError):
    pass