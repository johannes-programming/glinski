import string
import typing
from dataclasses import dataclass

from isometric import Vector

from .bitBoards import *
from .cells import *
from .cli import *
from .consts import *
from .errors import *
from .pieces import *
from .players import *

# __all__
__all__ = ['Board']


# global constants
FEN_RANKS = list(range(11, 0, -1))
OPTIONAL_PIECES = typing.Optional[Piece]

def neighborhoods(vectors:typing.Iterable[Vector]):
    ans = [BitBoard(0)] * 91
    for cell in Cell:
        search = cell.search(vectors)
        for s in search:
            ans[cell] |= s.flag
    ans = tuple(ans)
    return ans
KNIGHT_NEIGHBORHOODS = neighborhoods(consts.motions.HORSE)
KING_NEIGHBORHOODS = neighborhoods(
    list(consts.motions.LINE)
    + list(consts.motions.DIAGONAL)
)
WHITE_PAWN_ATTACK_NEIGHBORHOODS = neighborhoods(
    consts.motions.PAWN_ATTACKS_BY_PLAYER[Player.WHITE]
)
BLACK_PAWN_ATTACK_NEIGHBORHOODS = neighborhoods(
    consts.motions.PAWN_ATTACKS_BY_PLAYER[Player.BLACK]
)
PAWN_ATTACK_NEIGHBORHOODS_BY_PLAYER = {
    Player.WHITE:WHITE_PAWN_ATTACK_NEIGHBORHOODS,
    Player.BLACK:BLACK_PAWN_ATTACK_NEIGHBORHOODS,
}

# Board
@dataclass(frozen=True)
class BaseBoard:
    bitBoards:typing.Tuple[BitBoard]
class Board(BaseBoard):
    # methods
    #   dunder

    def __init__(self, 
        P=BitBoard(0),
        N=BitBoard(0),
        B=BitBoard(0),
        R=BitBoard(0),
        Q=BitBoard(0),
        K=BitBoard(0),
        p=BitBoard(0),
        n=BitBoard(0),
        b=BitBoard(0),
        r=BitBoard(0),
        q=BitBoard(0),
        k=BitBoard(0),
    ):
        bitBoards = [P, N, B, R, Q, K, p, n, b, r, q, k]
        bitBoards = [BitBoard(x) for x in bitBoards]
        bitBoards = tuple(bitBoards)
        taken = BitBoard(0)
        for bitBoard in bitBoards:
            if taken & bitBoard:
                raise ValueError
            taken |= bitBoard
        super().__init__(bitBoards=bitBoards)
    
    def __repr__(self) -> str:
        return self.text()
    def __str__(self) -> str:
        return self.text()


    #   public
    #     conversion
    #       fen
    @property
    def fen(self) -> str:
        ans = ""
        for rank in FEN_RANKS:
            empty = 0
            for f in range(11):
                file = File(f)
                if rank > file.height():
                    continue
                cell = Cell[file.name + str(rank)]
                piece = self.piece(cell)
                if piece is None:
                    empty += 1
                    continue
                if empty > 0:
                    ans += str(empty)
                    empty = 0
                ans += piece.fen()
            if empty > 0:
                ans += str(empty)
            ans += '/'
        ans = ans[:-1]
        return ans
    @classmethod
    def by_fen(cls, value:str) -> typing.Self:
        if type(value) is not str:
            raise TypeError(value)
        ans = 0
        parts = value.split('/')
        pieces = [None] * 91
        for rank, part in zip(FEN_RANKS, parts):
            empty = 0
            s = part
            for f in range(11):
                file = File(f)
                if file.height() < rank:
                    continue
                cell = Cell[file.name + str(rank)]
                j = 0
                while (j < len(s))and(s[j] in string.digits):
                    j += 1
                empty += int('0' + s[:j])
                s = s[j:]
                if empty > 0:
                    empty -= 1
                    continue
                pieces[cell] = Piece.by_fen(s[0])
                s = s[1:]
            if empty or s:
                raise ValueError(value)
        bitBoards = [BitBoard(0)] * 12
        for cell in Cell:
            if pieces[cell] is None:
                continue
            bitBoards[pieces[cell]] |= cell.flag
        ans = cls(bitBoards)
        return ans



    #     is-methods
    def is_check(self, turn:Player) -> bool:
        return bool(self.checkers(turn.opponent()))


    # 
    
    def apply(self, dictionary) -> typing.Self:
        cls = type(self)
        dictionary = dict(dictionary)
        dictionary = {Cell(k):v for k, v in dictionary.items()}
        bitBoards = list(self.bitBoards)
        applymask = BitBoard(0)
        for c in dictionary.keys():
            applymask |= c.flag
        nonemask = applymask.bitneg()
        for i in range(12):
            bitBoards[i] &= nonemask
        for c, p in dictionary.items():
            if p is None:
                continue
            piece = Piece(p)
            bitBoards[piece] |= BitBoard(c.flag)
        ans = cls(*bitBoards)
        return ans


        
    def attackers(self, 
        cell:Cell, *,
        player:typing.Optional[Player]=None,
    ) -> BitBoard:
        cell = Cell(cell)
        if player is None:
            player = self.piece(cell).player.opponent()
        elif type(player) is not Player:
            raise TypeError(player)

        ans = BitBoard(0)

        pawn = player * 6 + 0
        knight = player * 6 + 1
        bishop = player * 6 + 2
        rook = player * 6 + 3
        queen = player * 6 + 4
        king = player * 6 + 5

        pawn_neighborhoods = PAWN_ATTACK_NEIGHBORHOODS_BY_PLAYER[player.opponent()]
        ans |= self.bitBoards[pawn] & pawn_neighborhoods[cell]
        ans |= self.bitBoards[knight] & KNIGHT_NEIGHBORHOODS[cell]
        ans |= self.bitBoards[king] & KING_NEIGHBORHOODS[cell]
        
        diagonal_danger = self.bitBoards[bishop] | self.bitBoards[queen]
        line_danger = self.bitBoards[rook] | self.bitBoards[queen]
        modes = (
            (diagonal_danger, consts.motions.DIAGONAL),
            (line_danger, consts.motions.LINE),
        )
        occupied = self.occupied()

        for danger, motion in modes:
            for v in motion:
                for possible in cell.slide(v):
                    if possible.flag & danger:
                        ans |= possible.flag
                    if possible.flag & occupied:
                        break

        return ans
    


    def attacks(self,
        cell:Cell, *,
        piece:typing.Optional[Piece]=None,
    ) -> BitBoard:
        cell = Cell(cell)
        if piece is None:
            piece = self.piece(cell)
        else:
            piece = Piece(piece)
        if piece is None:
            return BitBoard(0)
        player = piece.player
        kind = piece.kind
        allowed = self.occupied(player).bitneg()
        
        if kind == 0:
            pawn_attack_neighborhoods = PAWN_ATTACK_NEIGHBORHOODS_BY_PLAYER[player]
            return allowed & pawn_attack_neighborhoods[cell]
        if kind == 1:
            return allowed & KNIGHT_NEIGHBORHOODS[cell]
        if kind == 5:
            return allowed & KING_NEIGHBORHOODS[cell]
        
        if kind == 2:
            vectors = consts.motions.DIAGONAL
        if kind == 3:
            vectors = consts.motions.LINE
        if kind == 4:
            vectors = set(consts.motions.DIAGONAL).union(consts.motions.LINE)
        
        occupied = self.occupied()
        ans = BitBoard(0)
        for v in vectors:
            for possible in cell.slide(v):
                if possible.flag & allowed:
                    ans |= possible.flag
                if possible.flag & occupied:
                    break
        return ans
    

    
    def checkers(self, player:Player) -> BitBoard: 
        ans = BitBoard(0)
        for c in Cell:
            p = self.piece(c)
            if p is None:
                continue
            if p.player == player:
                continue
            if p.kind != Piece.Kind.KING:
                continue
            ans |= self.attackers(
                c,
                player=player,
            )
        return ans



    def swapplayer(self) -> typing.Self: 
        cls = type(self)
        bitBoards = list(bitBoards)
        bitBoards = bitBoards[6:] + bitBoards[:6]
        for piece in Piece:
            bitBoards[piece] = bitBoards[piece].swapplayer()
        ans = cls(*bitBoards)
        return ans



    @classmethod
    def native(cls) -> typing.Self: 
        bitBoards = [BitBoard(0)] * 12
        for cell in Cell:
            piece = cell.native()
            if piece is None:
                continue
            bitBoards[piece] |= cell.flag
        ans = cls(*bitBoards)
        return ans
    


    def occupied(self, 
        player:typing.Optional[Player]=None,
    ) -> BitBoard:
        if player is None:
            a = 0
            b = 12
        else:
            player = Player(player)
            a = 6 * player
            b = 6 * (player + 1)
        ans = BitBoard(0)
        for i in range(a, b):
            ans |= self.bitBoards[i]
        return ans
    

    
    def piece(self, 
        cell:Cell,
    ) -> Piece: 
        cell = Cell(cell)
        flag = cell.flag
        for ans in Piece:
            if flag & self.bitBoards[ans]:
                return ans
            



    def text(self) -> str:
        symbols = ['.'] * 91
        for cell in Cell:
            piece = self.piece(cell)
            if piece is not None:
                symbols[cell] = piece.fen
        ans = cli.text(symbols)
        return ans




