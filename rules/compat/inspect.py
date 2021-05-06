from __future__ import absolute_import

try:
    from inspect import getfullargspec
except ImportError:
    # Python 2 compatibility
    from inspect import getargspec as getfullargspec  # noqa

from inspect import isfunction, ismethod  # noqa
