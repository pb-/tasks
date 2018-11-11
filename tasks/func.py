"""
Utility functions for functional concepts.
"""
from functools import partial, wraps
from collections import defaultdict


def valuedispatch(valuegetter=lambda args, kwargs: args[0].get('type')):
    """Like functools.singledispatch but for values."""
    def _valuedispatch(func):
        def _register(dispatch, value):
            def decorate(f):
                dispatch[value] = f
                return f
            return decorate

        dispatch = defaultdict(lambda: func)

        @wraps(func)
        def f(*args, **kwargs):
            value = valuegetter(args, kwargs)

            if value in dispatch:
                return dispatch[value](*args, **kwargs)

            return func(*args, **kwargs)

        f._dispatch = dispatch
        f.register = partial(_register, f._dispatch)

        return f

    return _valuedispatch
