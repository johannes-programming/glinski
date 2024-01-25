
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
    def dataGetattr(self, key:str):
        if key == 'setup':
            raise AttributeError(key)
        if key.startswith('__'):
            raise AttributeError(key)
        if key.startswith('_calc'):
            raise AttributeError(key)
        if not key.startswith('_'):
            return getattr(self, '_' + key)
        func = getattr(self, "_calc" + key)
        ans = func()
        setattr(self, key, ans)
        return ans



        



