# imports
import typing

from staticclasses import staticclass

from .cells_and_files import *

# __all__
__all__ = ['cli']




# class
class cli(staticclass):
    def __init__(self) -> None:
        raise NotImplementedError
    def text(symbols:typing.Iterable[str]):
        symbols = list(symbols)
        maxstrlen = 0
        for cell in Cell:
            symbols[cell] = str(symbols[cell])
            maxstrlen = max(maxstrlen, len(symbols[cell]))
        for cell in Cell:
            while len(symbols[cell]) < maxstrlen:
                symbols[cell] = ' ' + symbols[cell]
        particles = [
            ([' ' * maxstrlen] * 11) 
            for y in range(21)
        ]
        for cell in Cell:
            desc = cell.vector_from(Cell.f6).description()
            x = 5 + desc.y
            y = 10 + desc.y - (2 * desc.z)
            particles[y][x] = symbols[cell]
        spacer = ' ' * 3
        parts = [
            spacer.join(particles[y]) 
            for y in range(21)
        ]
        ans = '\n'.join(parts)
        return ans

       
        
    
