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
            fn, num_args, varargs, keywords, name = (fn.fn, fn.num_args,
                                                     fn.varargs, fn.keywords,
                                                     name or fn.name)
        elif inspect.isfunction(fn):
            argspec = inspect.getargspec(fn)
            num_args = len(argspec.args)
            varargs = argspec.varargs
            keywords = argspec.keywords
        elif isinstance(fn, object):
            callfn = getattr(fn, '__call__')
            argspec = inspect.getargspec(callfn)
            num_args = len(argspec.args) - 1  # skip `self`
            varargs = argspec.varargs
            keywords = argspec.keywords
            name = name or type(fn).__name__
        else:
            raise TypeError('Incompatible predicate.')
        assert num_args <= 2, 'Incompatible predicate.'
        self.fn = fn
        self.num_args = num_args
        self.varargs = varargs
        self.keywords = keywords
        self.name = name or fn.__name__
        self.siblings = None

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
        for predicate in self:
            try:
                inspect.getcallargs(predicate.fn, *args, **kwargs)
            except TypeError:
                continue
            else:
                return predicate.fn(*args, **kwargs)
        return self.fn(*args[:self.num_args], **kwargs)

    def __and__(self, other):
        def AND(*args, **kwargs):
            return self.test(*args, **kwargs) and other.test(*args, **kwargs)
        return type(self)(AND, '(%s & %s)' % (self.name, other.name))

    def __or__(self, other):
        def OR(*args, **kwargs):
            return self.test(*args, **kwargs) or other.test(*args, **kwargs)
        return type(self)(OR, '(%s | %s)' % (self.name, other.name))

    def __xor__(self, other):
        def XOR(*args, **kwargs):
            return self.test(*args, **kwargs) ^ other.test(*args, **kwargs)
        return type(self)(XOR, '(%s ^ %s)' % (self.name, other.name))

    def __invert__(self):
        def INVERT(*args, **kwargs):
            return not self.test(*args, **kwargs)
        if self.name.startswith('~'):
            name = self.name[1:]
        else:
            name = '~' + self.name
        return type(self)(INVERT, name)

    def test(self, *args, **kwargs):
        return bool(self(*args, **kwargs))

    def __iter__(self):
        if self.siblings is not None:
            for p in self.siblings:
                yield p
        else:
            yield self


def predicate_sort(predicate):
    """
    Elect predicates that have the most positional arg defined
    and return at last the one that have *args, and **kwargs in their
    signature.
    """
    return (predicate.num_args,
            predicate.varargs is None,
            predicate.keywords is None,
            )


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


def join_predicates(*args):
    """
    Bind predicates within a shared list.
    """
    siblings = []
    for p in args:
        assert p.siblings is None  # no multi group allowed
        p.siblings = siblings
        siblings.append(p)
    siblings.sort(key=predicate_sort, reverse=True)
