"""
memo.py

PURPOSE:
    Defines the @memo decorator class to cache function return values, improving performance for repeated computations (such as loading/resizing images).

HOW IT COMMUNICATES:
    - Used as a decorator on functions in photomosaic.py and related modules.
    - No direct file or database communication.

PATHS TO CHECK:
    - No paths or environment configuration needed.

MODERNIZATION NOTES:
    - For Python 3: uses collections.abc.Hashable.
    - Fully portable; no external dependencies outside stdlib.
"""

import collections.abc
import functools
import logging

logger = logging.getLogger(__name__)

class memo(object):
    """
    Decorator class for memoizing function outputs.
    Caches a function's return value each time it is called.
    If called again with the same arguments, the cached value is returned
    (not recomputed).
    Adapted from: http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.abc.Hashable):
            logger.warning("@memo decorator used with unhashable arguments. Skipping cache for: %s", args)
            return self.func(*args)
        if args in self.cache:
            logger.debug("Returning cached value for args: %s", args)
            return self.cache[args]
        else:
            logger.debug("Computing and caching value for args: %s", args)
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)