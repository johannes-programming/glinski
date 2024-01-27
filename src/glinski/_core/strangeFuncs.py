
import typing

from staticclasses import staticclass

# __all__
__all__ = ['strangeFuncs']




class strangeFuncs(staticclass):
    class IntModNew:
        def __init__(self, new, *, modulus):
            self._modulus = modulus
            self._new = new
        def __call__(self, cls, *args, **kwargs):
            v = int(*args, **kwargs)
            v %= self._modulus
            ans = self._new(cls, v)
            return ans
        


        



