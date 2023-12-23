from glinski._namedtuples.Departure import Departure as _Departure

from . import vectors as _vectors

KNIGHT = _Departure.from_units(
    _vectors.HORSEJUMP,
    rotate=True,
    maxfactor=1,
)

BISHOP = _Departure.from_units(
    _vectors.DIAGONAL,
    rotate=True,
)

ROOK = _Departure.from_units(
    _vectors.ROOK,
    rotate=True,
)

QUEEN = _Departure.from_units(
    _vectors.FILE,
    _vectors.DIAGONAL,
    rotate=True,
)

KING = _Departure.from_units(
    _vectors.FILE,
    _vectors.DIAGONAL,
    rotate=True,
    maxfactor=1,
)


