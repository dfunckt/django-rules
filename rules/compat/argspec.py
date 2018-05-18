try:
    from inspect import getfullargspec
except ImportError:
    # Python 2 compatibility
    from inspect import getargspec as getfullargspec
