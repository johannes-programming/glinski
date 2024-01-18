# imports
from __future__ import annotations

import typing
from dataclasses import dataclass

from .bitBoards import *
from .boards import *
from .cells import *
from .consts import *
from .errors import *
from .pieces import *
from .players import *
from .plies import *
from .terminations import *

# __all__
__all__ = ['Position']




# global constants
DEFAULT_BOARD = Board()




# classes
@dataclass
class PlyCharacter:
    subject:typing.Optional[Piece] = None
    target:typing.Optional[Piece] = None
    ep:bool = False
    null:bool = False
    def is_capture(self) -> bool:
        if self.target is not None:
            return True
        if self.ep:
            return True
        return False




@dataclass(frozen=True)
class BasePosition:
    board:Board
    ep_file:typing.Optional[File]
    turn:Player
class Position(BasePosition):

    # method
    #   dunder
    def __init__(self, *,
        board:Board=DEFAULT_BOARD,
        ep_file:typing.Optional[File]=None,
        turn:Player=Player.WHITE,
    ):
        if type(board) is not Board:
            raise TypeError(board)
        if ep_file is not None:
            ep_file = File(ep_file)
        turn = Player(turn)
        super().__init__(
            board=board,
            ep_file=ep_file,
            turn=turn,
        )




    #   protected
    
    def _plyCharacter(self, ply:Ply) -> PlyCharacter:
        if type(ply) is not Ply:
            raise TypeError(ply)
        ans = PlyCharacter()
        if ply.is_null():
            ans.null = True
            return ans
        ans.subject = self.board.piece(ply.from_cell)
        suspects = ply.suspects()
        if ans.subject not in suspects:
            raise NotPseudolegalError
        if ans.subject.player != self.turn:
            raise NotPseudolegalError
        ans.target = self.board.piece(ply.to_cell)
        if ans.target is not None:
            if ans.target.player == self.turn:
                raise NotPseudolegalError
        trajectory = ply.intermediates()
        for c in trajectory:
            if self.board.piece(c) is not None:
                raise NotPseudolegalError
        if ans.subject.kind != Piece.Kind.PAWN:
            return ans
        if ply.vector().digest().x:
            if self.ep_cell == ply.to_cell:
                ans.ep = True
            elif ans.target is None:
                raise NotPseudolegalError
        else:
            if ans.target is not None:
                raise NotPseudolegalError
        return ans
                




    #   public
    #     conversion
    @property
    def fen(self) -> str:
        parts = []
        parts.append(self.board.fen)
        parts.append(self.turn.fen)
        parts.append(self.ep_fen)
        ans = ' '.join(parts)
        return ans
    @classmethod
    def by_fen(cls, value:str, /) -> typing.Self:
        if type(value) is not str:
            raise TypeError(value)
        parts = value.split()
        board = Board.by_fen(parts[0])
        turn = Player.by_fen(parts[1])
        ep_cell = Cell.by_fen(parts[2])
        if ep_cell is None:
            ep_file = None
        else:
            ep_file = ep_cell.file
        ans = cls(
            board=board,
            turn=turn,
            ep_file=ep_file,
        )
        if ans.ep_cell != ep_cell:
            raise ValueError(value)
        return ans




    #     is
    def is_capture(self, ply:Ply) -> bool: # pseudolegal
        return self._plyCharacter(ply).is_capture()
    
    def is_checkmate(self) -> bool: 
        if not self.is_legal_check():
            return False
        return not len(self.legal_plies())

    def is_en_passant(self, ply:Ply) -> bool: # pseudolegal
        return self._plyCharacter(ply).ep

    def is_illegal_check(self) -> bool: # 
        return self.board.is_check(turn=self.turn.opponent())
    
    def is_legal(self) -> bool:
        if self.is_illegal_check():
            return False
        if self.ep_file in {File.a, File.l}:
            return False
        if self.ep_file is not None:
            walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
            attack_motion = consts.motions.PAWN_ATTACKS_BY_PLAYER[self.turn]
            further = self.ep_cell.apply(-walk)
            ep_victim = self.board.piece(further)
            if ep_victim != 6 * self.turn.opponent():
                return False
            ep_attacking_cells = set()
            for attack in attack_motion:
                ep_attacking_cells.add(further.apply(attack))
            ep_attackers = {self.board.piece(c) for c in ep_attacking_cells}
            if ep_victim.opponent() not in ep_attackers:
                return False
        kingthere = {player:False for player in Player}
        for c in Cell:
            p = self.board.piece(c)
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
    
    def is_legal_check(self) -> bool: # 
        return self.board.is_check(turn=self.turn)
        
    def is_legal_ply(self, ply:Ply) -> bool: # any
        if ply.is_null():
            return False
        if not self.is_pseudolegal_ply(ply):
            return False
        afterwards = self.apply(ply)
        ans = not afterwards.is_illegal_check()
        return ans
        
    def is_pseudolegal_ply(self, ply:Ply) -> bool: # any
        try:
            self._plyCharacter(ply)
        except NotPseudolegalError:
            return False
        else:
            return True
    
    def is_reversible(self, ply:Ply) -> bool: # pseudolegal
        character = self._plyCharacter(ply)
        if character.null:
            return True
        if character.subject.kind == Piece.Kind.PAWN:
            return False
        if character.is_capture():
            return False
        return True
        
    def is_stalemate(self) -> bool: # pseudolegal
        if self.is_legal_check():
            return False
        return not len(self.legal_plies())
    
    


    #     other
    def apply(self, ply:Ply): # pseudolegal
        cls = type(self)

        plyCharacter = self._plyCharacter(ply)
        if plyCharacter.null:
            return cls(
                board=self.board,
                ep_file=None,
                turn=self.turn.opponent(),
            )
        
        # board
        arrange = dict()
        arrange[ply.from_cell] = None
        if ply.promotion is None:
            arrange[ply.to_cell] = plyCharacter.subject
        else:
            arrange[ply.to_cell] = 6 * self.turn + ply.promotion
        if plyCharacter.ep:
            walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
            ep_victim_cell = self.ep_cell.apply(-walk)
            arrange[ep_victim_cell] = None
        board = self.board.apply(arrange)

        # ep_file
        ep_file = None
        if plyCharacter.subject.kind == Piece.Kind.PAWN:
            if abs(ply.vector()) == 2:
                walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
                attack_motion = consts.motions.PAWN_ATTACKS_BY_PLAYER[self.turn]
                for attack in attack_motion:
                    hand = walk + attack
                    try:
                        victimcell = ply.from_cell.apply(hand)
                    except:
                        continue
                    if self.board.piece(victimcell) != plyCharacter.subject.swapplayer():
                        continue
                    ep_file = ply.from_cell.file
                    break
        
        return cls(
            board=board,
            ep_file=ep_file,
            turn=self.turn.opponent(),
        )
    



    @property
    def ep_bitBoard(self) -> BitBoard:
        if self.ep_cell is None:
            return BitBoard(0)
        else:
            return BitBoard(self.ep_cell.flag)
    @property
    def ep_cell(self) -> typing.Optional[Cell]:
        if self.ep_file is None:
            return None
        return self.ep_file.ep_cell(self.turn)
    @property
    def ep_fen(self) -> str:
        c = self.ep_cell
        if c is None:
            return '-'
        else:
            return c.fen()
    



    def legal_plies(self) -> typing.Set[Ply]:
        ans = set()
        for ply in self.pseudolegal_plies():
            afterwards = self.apply(ply)
            if not afterwards.is_illegal_check():
                ans.add(ply)
        return ans
            



    @classmethod
    def native(cls):
        return cls(
            board=Board.native(),
            ep_file=None,
            turn=Player.WHITE,
        )
    



    def pseudolegal_plies(self) -> typing.Set[Ply]:
        ans = {Ply.null()}
        for c in Cell:
            p = self.board.piece(c)
            if p is None:
                continue
            if p.player != self.turn:
                continue
            if p.kind != Piece.Kind.PAWN:
                to_cells = self.board.attacks(c)
                for to_cell in Cell:
                    if to_cells & to_cell.flag:
                        ply = Ply(
                            from_cell=c,
                            to_cell=to_cell,
                            promotion=None,
                        )
                        ans.add(ply)
                continue

            to_cells = 0
            to_cells = self.board.occupied(self.turn.opponent())
            to_cells |= self.ep_bitBoard
            to_cells &= self.board.attacks(c)
            occupied = self.board.occupied()
            walk = consts.vectors.PAWN_WALKS_BY_PLAYER[self.turn]
            generator = c.count_up(start=1, stop=3, vector=walk)
            for n, advance in generator:
                if occupied & advance.flag:
                    break
                if n == 1:
                    to_cells |= advance.flag
                    continue
                elif c.native() == self.board.piece(c):
                    to_cells |= advance.flag
                break
            to_cells = BitBoard(to_cells)
            for to_cell in Cell:
                if not (to_cell.flag & to_cells):
                    continue
                if not to_cell.promotion(self.turn):
                    ply = Ply(
                        from_cell=c,
                        to_cell=to_cell,
                        promotion=None,
                    )
                    ans.add(ply)
                    continue
                for p in range(1, 5):
                    ply = Ply(
                        from_cell=c,
                        to_cell=to_cell,
                        promotion=Piece.Kind(p),
                    )
                    ans.add(ply)
        return ans
    



    def termination(self):
        if len(self.legal_plies()):
            return None
        if self.is_legal_check():
            kind = Termination.Kind.CHECKMATE
        else:
            kind = Termination.Kind.STALEMATE
        ans = Termination(
            kind=kind,
            subject=self.turn.opponent(),
        )
        return ans
    







