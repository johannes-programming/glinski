from __future__ import annotations

import typing
from dataclasses import asdict, dataclass

from glinski._consts import *
from glinski._enums import *
from glinski._errors import *

from .arrangements import *
from .moveCharacters import *
from .moves import *
from .pieces import *
from .terminations import *

__all__ = ['Position']



DEFAULT_ARRANGEMENT = Arrangement()

@dataclass(frozen=True)
class BasePosition:

    # fields
    arrangement:Arrangement
    ep_column:typing.Optional[Column]
    turn:Player

    # method

    #   protected
    
    def _moveCharacter(self, move:Move) -> MoveCharacter:
        if type(move) is not Move:
            raise TypeError(move)
        ans = MoveCharacter()
        ans.subject = self.arrangement[move.from_cell]
        suspects = move.suspects()
        if ans.subject not in suspects:
            raise UnsoundMoveError
        if ans.subject.player != self.turn:
            raise UnsoundMoveError
        ans.target = self.arrangement[move.to_cell]
        if ans.target is not None:
            if ans.target.player == self.turn:
                raise UnsoundMoveError
        trajectory = move.trajectory()[1:]
        for c in trajectory:
            if self.arrangement[c] is not None:
                raise UnsoundMoveError
        if ans.subject.kind != Piece.Kind.PAWN:
            return ans
        if move.vector().digest().x:
            if self.ep_cell() == move.to_cell:
                ans.ep = True
            elif ans.target is None:
                raise UnsoundMoveError
        else:
            if ans.target is not None:
                raise UnsoundMoveError
        return ans
                
    def _pawn_to_cells(self, 
        pawncell:Cell,
    ) -> typing.Generator[Cell, None, None]:
        attacks = self.arrangement.attacks(pawncell)
        for a in attacks:
            if a == self.ep_cell():
                yield a
                continue
            if self.arrangement[a] is None:
                continue
            yield a
        walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
        generator = pawncell.count_up(start=1, stop=3, vector=walk)
        for n, advance in generator:
            if self.arrangement[advance] is not None:
                break
            elif n == 1:
                yield advance
            elif pawncell.native() != self.arrangement[pawncell]:
                break
            elif self.arrangement[advance] is not None:
                break
            else:
                yield advance
                    






    #   public

    def apply(self, move:Move):
        cls = type(self)

        moveCharacter = self._moveCharacter(move)
        
        # arrangement
        arrange = dict()
        arrange[move.from_cell] = None
        if move.promotion is None:
            arrange[move.to_cell] = moveCharacter.subject
        else:
            arrange[move.to_cell] = Piece(
                kind=move.promotion,
                player=self.turn,
            )
        if moveCharacter.ep:
            walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
            ep_victim_cell = self.ep_cell().apply(-walk)
            arrange[ep_victim_cell] = None
        arrangement = self.arrangement.apply(arrange)

        # ep_column
        ep_column = None
        if moveCharacter.subject.kind == Piece.Kind.PAWN:
            if abs(move.vector()) == 2:
                walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
                attack_motion = consts.motions.PAWN_ATTACKS_BY_PLAYER[self.turn]
                for attack in attack_motion:
                    hand = walk + attack
                    try:
                        victimcell = move.from_cell.apply(hand)
                    except ValueError:
                        continue
                    if self.arrangement[victimcell] != moveCharacter.subject.invert():
                        continue
                    ep_column = move.from_cell.column()
                    break
        
        return cls(
            arrangement=arrangement,
            ep_column=ep_column,
            turn=self.turn.invert(),
        )

    def ep_cell(self) -> typing.Optional[Cell]:
        if self.ep_column is None:
            return None
        return self.ep_column.ep_cell(self.turn)
    


    def is_anticheck(self) -> bool:
        return self.arrangement.is_check(turn=self.turn.invert())
    
    def is_capture(self, move:Move) -> bool:
        return self._moveCharacter(move).is_capture()
    
    def is_check(self) -> bool:
        return self.arrangement.is_check(turn=self.turn)
    
    def is_checkmate(self) -> bool:
        if not self.is_check():
            return False
        return not len(self.legal_moves())

    def is_en_passant(self, move:Move) -> bool:
        return self._moveCharacter(move).ep
    
    def is_legal(self) -> bool:
        if self.is_anticheck():
            return False
        if self.ep_column in {Column.a, Column.l}:
            return False
        if self.ep_column is not None:
            walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
            attack_motion = consts.motions.PAWN_ATTACKS_BY_PLAYER[self.turn]
            further = self.ep_cell().apply(-walk)
            ep_victim = self.arrangement[further]
            if ep_victim != Piece(kind=Piece.Kind.PAWN, player=self.turn.invert()):
                return False
            ep_attacking_cells = set()
            for attack in attack_motion:
                ep_attacking_cells.add(further.apply(attack))
            ep_attackers = {self.arrangement[c] for c in ep_attacking_cells}
            if ep_victim.invert() not in ep_attackers:
                return False
        kingthere = {player:False for player in Player}
        for c, p in self.arrangement.items():
            if p is None:
                continue
            if p.kind == Piece.Kind.KING:
                if kingthere[p.player]:
                    return False
                kingthere[p.player] = True
            if p.kind == Piece.Kind.PAWN:
                if not c.pawn_legal(p.player):
                    return False
        if not all(kingthere.values()):
            return False
        return True
        
    def is_legal_move(self, move:Move) -> bool:
        if not self.is_sound_move(move):
            return False
        afterwards = self.apply(move)
        ans = not afterwards.is_anticheck()
        return ans
        
    def is_sound_move(self, move:Move) -> bool:
        try:
            self._moveCharacter(move)
        except UnsoundMoveError:
            return False
        else:
            return True
        
    def is_stalemate(self) -> bool:
        if self.is_check():
            return False
        return not len(self.legal_moves())
    
    def is_zeroing(self, move:Move) -> bool:
        character = self._moveCharacter(move)
        if character.subject.kind == Piece.Kind.PAWN:
            return True
        if character.is_capture():
            return True
        return False
    



    def legal_moves(self) -> typing.Set[Move]:
        ans = set()
        for move in self.sound_moves():
            afterwards = self.apply(move)
            if not afterwards.is_anticheck():
                ans.add(move)
        return ans
            
    @classmethod
    def native(cls):
        return cls(
            arrangement=Arrangement.native(),
            ep_column=None,
            turn=Player.WHITE,
        )
    
    def replace(self, **kwargs) -> typing.Self:
        cls = type(self)
        dictionary = asdict(self)
        dictionary.update(kwargs)
        ans = cls(**dictionary)
        return ans

    def sound_moves(self) -> typing.Set[Move]:
        ans = set()
        for c, p in self.arrangement.items():
            if p is None:
                continue
            if p.player != self.turn:
                continue
            if p.kind != Piece.Kind.PAWN:
                to_cells = self.arrangement.attacks(c)
                for to_cell in to_cells:
                    move = Move(
                        from_cell=c,
                        to_cell=to_cell,
                        promotion=None,
                    )
                    ans.add(move)
                continue
            to_cells = self._pawn_to_cells(pawncell=c)
            for to_cell in to_cells:
                if not to_cell.promotion(self.turn):
                    move = Move(
                        from_cell=c,
                        to_cell=to_cell,
                        promotion=None,
                    )
                    ans.add(move)
                    continue
                for promotion in Piece.Kind.promotions():
                    move = Move(
                        from_cell=c,
                        to_cell=to_cell,
                        promotion=promotion,
                    )
                    ans.add(move)
        return ans
    
    def termination(self):
        if len(self.position().legal_moves()):
            return None
        if self.position().is_check():
            kind = Termination.Kind.CHECKMATE
        else:
            kind = Termination.Kind.STALEMATE
        ans = Termination(
            kind=kind,
            subject=self.turn.invert(),
        )
        return ans
    










class Position(BasePosition):
    def __init__(self, *,
        arrangement:Arrangement=DEFAULT_ARRANGEMENT,
        ep_column:typing.Optional[Column]=None,
        turn:Player=Player.WHITE,
    ):
        if type(arrangement) is not Arrangement:
            raise TypeError(arrangement)
        if type(ep_column) is not Column:
            if ep_column is not None:
                raise TypeError(ep_column)
        if type(turn) is not Player:
            raise TypeError(turn)
        super().__init__(
            arrangement=arrangement,
            ep_column=ep_column,
            turn=turn,
        )

