import typing

from isometric import Vector

from glinski import _consts
from glinski._enums import *
from glinski._errors import *
from glinski._namedtuples.Departure import *
from glinski._namedtuples.Move import *

from .Arrangement import *
from .Move import *

__all__ = ['Situation']


class Situation(typing.NamedTuple):

    # fields
    arrangement:Arrangement = Arrangement()
    currentPlayer:Player = Player.WHITE
    boredom:int = 0
    pawnpassing:typing.Union[Column, None] = None


    # operators
    def __eq__(self, other) -> bool:
        cls = type(self)
        if type(other) is not cls:
            return False
        return super().__eq__(other)
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    def __post_init__(self, *args, **kwargs):
        if type(self.arrangement) is not Arrangement:
            raise TypeError(self.arrangement)
        if type(self.currentPlayer) is not Player:
            raise TypeError(self.currentPlayer)
        if type(self.boredom) is not int:
            raise TypeError(self.boredom)
        if not (0 <= self.boredom <= 100):
            raise ValueError(self.boredom)
        if self.pawnpassing is None:
            return
        if type(self.pawnpassing) is not Column:
            raise TypeError(self.pawnpassing)


    
    # methods
    def _apply(self, move:Move) -> typing.Self:
        """This method assumes that the move is valid (but not that it is legal). """
        # aux variables
        actorType = self._pieceType(move.start)
        victim = self._pieceKind(move.stop)
        path = move.stop.value - move.start.value
        if self.currentPlayer == Player.WHITE:
            pawnwalk = Vector(z=1)
        else:
            pawnwalk = Vector(z=-1)
        pawnattacks = [pawnwalk.rotate(-1), pawnwalk.rotate(1)]
        if bool(path):
            scale, hint = path.factorize()
        else:
            scale = None
            hint = None

        # the actual application of the move
        ans = self._replace(currentPlayer=self.currentPlayer.invert())
        if (actorType == PieceType.PAWN) and (scale == 2):
            ans = ans._replace(pawnpassing=move.stop.column())
        else:
            ans = ans._replace(pawnpassing=None)
        if (actorType == PieceType.PAWN) or (victim is not None):
            ans = ans._replace(boredom=0)
        else:
            ans = ans._replace(boredom=ans.boredom+1)
        kwargs = dict()
        if move.promotion is None:
            kwargs[move.stop.name] = kwargs[move.start.name]
        else:
            kwargs[move.stop.name] = move.promotion
        kwargs[move.start.name] = None
        if actorType == PieceType.PAWN:
            if hint in pawnattacks:
                if victim is None:
                    eptarget = Cell(move.stop.value - pawnwalk)
                    kwargs[eptarget.name] = None
        arrangement = ans.arrangement._replace(**kwargs)
        ans._replace(arrangement=arrangement)
        return ans



    def _depart(self, departure:Departure, origin:Cell):
        for direction in departure.directions(origin):
            for cell in direction:
                pieceKind = self._pieceKind(cell)
                if pieceKind is None:
                    yield cell
                    continue
                if pieceKind.player() != self.currentPlayer:
                    yield cell
                break



        
    def _epstop(self):
        if self.pawnpassing is None:
            return None
        return self.pawnpassing.pawnpassing(self.currentPlayer.invert())
    

    
    def _moves(self):
        for originname, pieceKind in self.arrangement._asdict().items():
            if pieceKind is None:
                continue
            if pieceKind.player() != self.currentPlayer:
                continue
            pieceType = pieceKind.pieceType()
            origin = Cell[originname]
            if pieceType == PieceType.PAWN:
                for pawn_stop in self._pawn_stops(origin):
                    if pawn_stop.promotion(self.currentPlayer):
                        promotions = PieceType.promotions()
                    else:
                        promotions = [None]
                    for promotion in promotions:
                        yield Move(
                            start=origin,
                            stop=pawn_stop,
                            promotion=promotion,
                        )
                raise NotImplementedError
            else:
                departure = getattr(_consts.departures, pieceType.name)
                for cell in self._depart(departure, origin=origin):
                    yield Move(
                        start=origin,
                        stop=cell,
                        promotion=None,
                    )    


    def _pawn_stops(self, origin:Cell):                    
        if self.currentPlayer == Player.WHITE:
            pawn_walk_vector = _consts.vectors.WHITE_PAWN_WALK
        else:
            pawn_walk_vector = _consts.vectors.BLACK_PAWN_WALK
        for n in [1, 2]:
            cellvector = origin.value + (n * pawn_walk_vector)
            try:
                cell = Cell(cellvector)
            except ValueError:
                break
            pieceKind = self._pieceKind(cell)
            if pieceKind is not None:
                break    
            yield cell
            if pieceKind != origin.native():
                break
        for s in [-1, 1]:
            cellvector = origin.value + pawn_walk_vector.rotate(s)
            try:
                cell = Cell(cellvector)
            except ValueError:
                continue
            if cell == self._epstop():
                yield cell
                continue
            pieceKind = self._pieceKind(cell)
            if pieceKind is None:
                continue
            if pieceKind.player == self.currentPlayer:
                continue   
            yield cell

        
    
    def _pieceKind(self, key, /) -> typing.Union[PieceKind, None]:
        if type(key) is Cell:
            key = key.name
        if type(key) is str:
            return getattr(self.arrangement, key)
        raise TypeError
    
    def _pieceType(self, key) -> typing.Union[PieceType, None]:
        k = self._pieceKind(key)
        if k is None:
            return None
        return k.pieceType()



    def _validate(self, move:Move) -> typing.Self:
        # aux variables
        actor = self._pieceKind(move.start)
        actorType = self._pieceType(move.start)
        victim = self._pieceKind(move.stop)
        path = move.stop.value - move.start.value
        if self.currentPlayer == Player.WHITE:
            pawnwalk = Vector(z=1)
        else:
            pawnwalk = Vector(z=-1)
        pawnattacks = [pawnwalk.rotate(-1), pawnwalk.rotate(1)]
        if bool(path):
            scale, hint = path.factorize()
            radius = float(abs(hint))
        else:
            scale = None
            hint = None
            radius = None
        # the actual validation
        #   start == stop
        if move.start == move.stop:
            raise InvalidMoveError
        #   50 moves
        if self.boredom == 100:
            raise InvalidMoveError
        #   start
        if actor is None:
            raise InvalidMoveError
        if actor.player() != self.currentPlayer:
            raise InvalidMoveError
        #   stop
        if victim is not None:
            if victim.player() == self.currentPlayer:
                raise InvalidMoveError
        #   promotion
        if move.promotion is not None:
            if not move.promotion.promotion():
                raise InvalidMoveError
            if not move.stop.promotion(self.currentPlayer):
                raise InvalidMoveError
            if actorType != PieceType.PAWN:
                raise InvalidMoveError
        elif move.stop.promotion(self.currentPlayer) and (actorType == PieceType.PAWN):
            raise InvalidMoveError
        #   path
        for i in range(1, scale):
            cellvalue = (hint * i) + move.start
            cellname = Cell(cellvalue).name
            obstacle = getattr(self.arrangement, cellname)
            if obstacle is not None:
                raise InvalidMoveError
        #   does the piece move like its type demand?
        if actorType != PieceType.PAWN:
            departure = getattr(_consts.departures, actorType.name)
            if radius not in departure.radii():
                raise InvalidMoveError
            if scale > departure.maxfactor:
                raise InvalidMoveError
        else:
            if scale > 2:
                raise InvalidMoveError
            if scale == 2:
                if hint != pawnwalk:
                    raise InvalidMoveError
                if move.start.native() != actor:
                    raise InvalidMoveError
            if hint == pawnwalk:
                if victim is not None:
                    raise InvalidMoveError
            elif hint in pawnattacks:
                if (victim is None) and (self._epstop() != move.stop):
                    raise InvalidMoveError
            else:
                raise InvalidMoveError




    def apply(self, move:Move) -> typing.Self:
        self._validate(move)
        ans = self._apply(move)
        if ans.arrangement.check(ans.currentPlayer):
            raise UnresolvedCheckError
        return ans

    def invert(self):
        cls = type(self)
        return cls(
            arrangement=self.arrangement.invert(),
            currentPlayer=self.currentPlayer.invert(),
            pawnpassing=self.pawnpassing,
        )
        
        





