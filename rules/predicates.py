import logging
import operator
import threading
from functools import partial, update_wrapper
from inspect import getfullargspec, isfunction, ismethod
from typing import Any, Callable, List, Optional, Tuple, Union

logger = logging.getLogger("rules")


def assert_has_kwonlydefaults(fn: Callable[..., Any], msg: str) -> None:
    argspec = getfullargspec(fn)
    if hasattr(argspec, "kwonlyargs"):
        if not argspec.kwonlyargs:
            return
        if not argspec.kwonlydefaults or len(argspec.kwonlyargs) > len(
            argspec.kwonlydefaults.keys()
        ):
            raise TypeError(msg)


class Context(dict):
    def __init__(self, args: Tuple[Any, ...]) -> None:
        super(Context, self).__init__()
        self.args = args


class localcontext(threading.local):
    def __init__(self) -> None:
        self.stack: List[Context] = []


_context = localcontext()


class NoValueSentinel(object):
    def __bool__(self) -> bool:
        return False

    __nonzero__ = __bool__  # python 2


NO_VALUE = NoValueSentinel()

del NoValueSentinel


class Predicate(object):
    fn: Callable[..., Any]
    num_args: int
    var_args: bool
    name: str

    def __init__(
        self,
        fn: Union["Predicate", Callable[..., Any]],
        name: Optional[str] = None,
        bind: bool = False,
    ) -> None:
        # fn can be a callable with any of the following signatures:
        #   - fn(obj=None, target=None)
        #   - fn(obj=None)
        #   - fn()
        assert callable(fn), "The given predicate is not callable."
        innerfn = fn
        if isinstance(fn, Predicate):
            innerfn, num_args, var_args, name = (
                fn.fn,
                fn.num_args,
                fn.var_args,
                name or fn.name,
            )
            fn = innerfn
        elif isinstance(fn, partial):
            innerfn = fn.func
            argspec = getfullargspec(innerfn)
            var_args = argspec.varargs is not None
            num_args = len(argspec.args) - len(fn.args)
            if ismethod(innerfn):
                num_args -= 1  # skip `self`
            name = fn.func.__name__
        elif ismethod(fn):
            argspec = getfullargspec(fn)
            var_args = argspec.varargs is not None
            num_args = len(argspec.args) - 1  # skip `self`
        elif isfunction(fn):
            argspec = getfullargspec(fn)
            var_args = argspec.varargs is not None
            num_args = len(argspec.args)
        elif isinstance(fn, object):
            innerfn = getattr(fn, "__call__")  # noqa
            argspec = getfullargspec(innerfn)
            var_args = argspec.varargs is not None
            num_args = len(argspec.args) - 1  # skip `self`
            name = name or type(fn).__name__
        else:  # pragma: no cover
            # We handle all cases, so there's no way we can reach here
            raise TypeError("Incompatible predicate.")
        if bind:
            num_args -= 1
        assert_has_kwonlydefaults(
            innerfn,
            "The given predicate is missing defaults for keyword-only arguments",
        )
        assert num_args <= 2, "Incompatible predicate."
        self.fn = fn
        self.num_args = num_args
        self.var_args = var_args
        self.name = name or fn.__name__
        self.bind = bind

    def __repr__(self) -> str:
        return "<%s:%s object at %s>" % (type(self).__name__, str(self), hex(id(self)))

    def __str__(self) -> str:
        return self.name

    def __call__(self, *args, **kwargs) -> Any:
        # this method is defined as variadic in order to not mask the
        # underlying callable's signature that was most likely decorated
        # as a predicate. internally we consistently call ``_apply`` that
        # provides a single interface to the callable.
        if self.bind:
            return self.fn(self, *args, **kwargs)
        return self.fn(*args, **kwargs)

    @property
    def context(self) -> Optional[Context]:
        """
        The currently active invocation context. A new context is created as a
        result of invoking ``test()`` and is only valid for the duration of
        the invocation.

        Can be used by predicates to store arbitrary data, eg. for caching
        computed values, setting flags, etc., that can be used by predicates
        later on in the chain.

        Inside a predicate function it can be used like so::

            >>> @predicate
            ... def mypred(a, b):
            ...     value = compute_expensive_value(a)
            ...     mypred.context['value'] = value
            ...     return True
            ...

        Other predicates can later use stored values::

            >>> @predicate
            ... def myotherpred(a, b):
            ...     value = myotherpred.context.get('value')
            ...     if value is not None:
            ...         return do_something_with_value(value)
            ...     else:
            ...         return do_something_without_value()
            ...

        """
        try:
            return _context.stack[-1]
        except IndexError:
            return None

    def test(self, obj: Any = NO_VALUE, target: Any = NO_VALUE) -> bool:
        """
        The canonical method to invoke predicates.
        """
        args = tuple(arg for arg in (obj, target) if arg is not NO_VALUE)
        _context.stack.append(Context(args))
        logger.debug("Testing %s", self)
        try:
            return bool(self._apply(*args))
        finally:
            _context.stack.pop()

    def __and__(self, other) -> "Predicate":
        def AND(*args):
            return self._combine(other, operator.and_, args)

        return type(self)(AND, "(%s & %s)" % (self.name, other.name))

    def __or__(self, other) -> "Predicate":
        def OR(*args):
            return self._combine(other, operator.or_, args)

        return type(self)(OR, "(%s | %s)" % (self.name, other.name))

    def __xor__(self, other) -> "Predicate":
        def XOR(*args):
            return self._combine(other, operator.xor, args)

        return type(self)(XOR, "(%s ^ %s)" % (self.name, other.name))

    def __invert__(self) -> "Predicate":
        def INVERT(*args):
            result = self._apply(*args)
            return None if result is None else not result

        if self.name.startswith("~"):
            name = self.name[1:]
        else:
            name = "~" + self.name
        return type(self)(INVERT, name)

    def _combine(self, other, op, args):
        self_result = self._apply(*args)
        if self_result is None:
            return other._apply(*args)

        # short-circuit evaluation
        if op is operator.and_ and not self_result:
            return False
        elif op is operator.or_ and self_result:
            return True

        other_result = other._apply(*args)
        if other_result is None:
            return self_result

        return op(self_result, other_result)

    def _apply(self, *args) -> Optional[bool]:
        # Internal method that is used to invoke the predicate with the
        # proper number of positional arguments, inside the current
        # invocation context.
        if self.var_args:
            callargs = args
        elif self.num_args > len(args):
            callargs = args + (None,) * (self.num_args - len(args))
        else:
            callargs = args[: self.num_args]
        if self.bind:
            callargs = (self,) + callargs

        result = self.fn(*callargs)
        result = None if result is None else bool(result)

        logger.debug("  %s = %s", self, "skipped" if result is None else result)
        return result


def predicate(fn=None, name=None, **options):
    """
    Decorator that constructs a ``Predicate`` instance from any function::

        >>> @predicate
        ... def is_book_author(user, book):
        ...     return user == book.author
        ...

        >>> @predicate(bind=True)
        ... def is_book_author(self, user, book):
        ...     if self.context.args:
        ...         return user == book.author
    """
    if not name and not callable(fn):
        name = fn
        fn = None

    def inner(fn):
        if isinstance(fn, Predicate):
            return fn
        p = Predicate(fn, name, **options)
        update_wrapper(p, fn)
        return p

    if fn:
        return inner(fn)
    else:
        return inner


# Predefined predicates

always_true = predicate(lambda: True, name="always_true")
always_false = predicate(lambda: False, name="always_false")

always_allow = predicate(lambda: True, name="always_allow")
always_deny = predicate(lambda: False, name="always_deny")


def is_bool_like(obj) -> bool:
    return hasattr(obj, "__bool__") or hasattr(obj, "__nonzero__")


@predicate
def is_authenticated(user) -> bool:
    if not hasattr(user, "is_authenticated"):
        return False  # not a user model
    if not is_bool_like(user.is_authenticated):  # pragma: no cover
        # Django < 1.10
        return user.is_authenticated()
    return user.is_authenticated


@predicate
def is_superuser(user) -> bool:
    if not hasattr(user, "is_superuser"):
        return False  # swapped user model, doesn't support is_superuser
    return user.is_superuser


@predicate
def is_staff(user) -> bool:
    if not hasattr(user, "is_staff"):
        return False  # swapped user model, doesn't support is_staff
    return user.is_staff


@predicate
def is_active(user) -> bool:
    if not hasattr(user, "is_active"):
        return False  # swapped user model, doesn't support is_active
    return user.is_active


def is_group_member(*groups) -> Callable[..., Any]:
    assert len(groups) > 0, "You must provide at least one group name"

    if len(groups) > 3:
        g = groups[:3] + ("...",)
    else:
        g = groups

    name = "is_group_member:%s" % ",".join(g)

    @predicate(name)
    def fn(user) -> bool:
        if not hasattr(user, "groups"):
            return False  # swapped user model, doesn't support groups
        if not hasattr(user, "_group_names_cache"):  # pragma: no cover
            user._group_names_cache = set(user.groups.values_list("name", flat=True))
        return set(groups).issubset(user._group_names_cache)

    return fn
