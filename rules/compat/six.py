import functools
import sys


if sys.version_info[0] == 3:
    string_types = str,
else:
    string_types = basestring,

if sys.version_info[0:2] < (3, 4):
    def wraps(wrapped, assigned=functools.WRAPPER_ASSIGNMENTS,
              updated=functools.WRAPPER_UPDATES):
        def wrapper(f):
            f = functools.wraps(wrapped, assigned, updated)(f)
            f.__wrapped__ = wrapped
            return f
        return wrapper
else:
    wraps = functools.wraps
