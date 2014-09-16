import inspect
from functools import update_wrapper


class Predicate(object):
    def __init__(self, fn, name=None):
        # fn can be a callable with any of the following signatures:
        #   - fn(obj=None, target=None)
        #   - fn(obj=None)
        #   - fn()
        assert callable(fn), 'The given predicate is not callable.'
        if isinstance(fn, Predicate):
            fn, num_args, name = fn.fn, fn.num_args, name or fn.name
        elif inspect.isfunction(fn):
            num_args = len(inspect.getargspec(fn).args)
        elif isinstance(fn, object):
            callfn = getattr(fn, '__call__')
            num_args = len(inspect.getargspec(callfn).args) - 1  # skip `self`
            name = name or type(fn).__name__
        else:
            raise TypeError('Incompatible predicate.')
        assert num_args <= 2, 'Incompatible predicate.'
        self.fn = fn
        self.num_args = num_args
        self.name = name or fn.__name__

    def __repr__(self):
        return '<%s:%s object at %s>' % (
            type(self).__name__, str(self), hex(id(self)))

    def __str__(self):
        return self.name

    def __call__(self, *args, **kwargs):
        # this method is defined as variadic in order to not mask the
        # underlying callable's signature that was most likely decorated
        # as a predicate. internally we consistently call ``test`` that
        # provides a single interface to the callable.
        return self.fn(*args, **kwargs)

    def __and__(self, other):
        def AND(obj=None, target=None):
            return self.test(obj, target) and other.test(obj, target)
        return type(self)(AND, '(%s & %s)' % (self.name, other.name))

    def __or__(self, other):
        def OR(obj=None, target=None):
            return self.test(obj, target) or other.test(obj, target)
        return type(self)(OR, '(%s | %s)' % (self.name, other.name))

    def __xor__(self, other):
        def XOR(obj=None, target=None):
            return self.test(obj, target) ^ other.test(obj, target)
        return type(self)(XOR, '(%s ^ %s)' % (self.name, other.name))

    def __invert__(self):
        def INVERT(obj=None, target=None):
            return not self.test(obj, target)
        if self.name.startswith('~'):
            name = self.name[1:]
        else:
            name = '~' + self.name
        return type(self)(INVERT, name)

    def test(self, obj=None, target=None):
        # we setup a list of function args depending on the number of
        # arguments accepted by the underlying callback.
        if self.num_args == 2:
            args = (obj, target)
        elif self.num_args == 1:
            args = (obj,)
        else:
            args = ()
        return bool(self.fn(*args))


def predicate(fn=None, name=None):
    """
    Decorator that constructs a ``Predicate`` instance from any function::

        >>> @predicate
        ... def is_book_author(user, book):
        ...     return user == book.author
        ...
    """
    if not name and not callable(fn):
        name = fn
        fn = None

    def inner(fn):
        if isinstance(fn, Predicate):
            return fn
        p = Predicate(fn, name)
        update_wrapper(p, fn)
        return p

    if fn:
        return inner(fn)
    else:
        return inner


# Predefined predicates

always_true = predicate(lambda: True, name='always_true')
always_false = predicate(lambda: False, name='always_false')

always_allow = predicate(lambda: True, name='always_allow')
always_deny = predicate(lambda: False, name='always_deny')


@predicate
def is_authenticated(user):
    if not hasattr(user, 'is_authenticated'):
        return False  # not a user model
    return user.is_authenticated()


@predicate
def is_superuser(user):
    if not hasattr(user, 'is_superuser'):
        return False  # swapped user model, doesn't support is_superuser
    return user.is_superuser


@predicate
def is_staff(user):
    if not hasattr(user, 'is_staff'):
        return False  # swapped user model, doesn't support is_staff
    return user.is_staff


@predicate
def is_active(user):
    if not hasattr(user, 'is_active'):
        return False  # swapped user model, doesn't support is_active
    return user.is_active


def is_group_member(*groups):
    assert len(groups) > 0, 'You must provide at least one group name'

    if len(groups) > 3:
        g = groups[:3] + ('...',)
    else:
        g = groups

    name = 'is_group_member:%s' % ','.join(g)

    @predicate(name)
    def fn(user):
        if not hasattr(user, 'groups'):
            return False  # swapped user model, doesn't support groups
        if not hasattr(user, '_group_names_cache'):
            user._group_names_cache = set(user.groups.values_list('name', flat=True))
        return set(groups).issubset(user._group_names_cache)

    return fn
