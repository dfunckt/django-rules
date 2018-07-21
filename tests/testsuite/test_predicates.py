import sys
import functools
from unittest import TestCase

from rules.predicates import (
    NO_VALUE,
    Predicate,
    always_allow,
    always_deny,
    always_false,
    always_true,
    predicate,
)

if sys.version_info >= (3,):
    from ._test_predicates_kwonly import *


class PredicateTests(TestCase):
    def test_always_true(self):
        assert always_true()

    def test_always_false(self):
        assert not always_false()

    def test_always_allow(self):
        assert always_allow()

    def test_always_deny(self):
        assert not always_deny()

    def test_lambda_predicate(self):
        p = Predicate(lambda x: x == 'a')
        assert p.name == '<lambda>'
        assert p.num_args == 1
        assert p('a')

    def test_lambda_predicate_custom_name(self):
        p = Predicate(lambda x: x == 'a', name='mypred')
        assert p.name == 'mypred'
        assert p.num_args == 1
        assert p('a')

    def test_function_predicate(self):
        def mypred(x):
            return x == 'a'
        p = Predicate(mypred)
        assert p.name == 'mypred'
        assert p.num_args == 1
        assert p('a')

    def test_function_predicate_custom_name(self):
        def mypred(x):
            return x == 'a'
        p = Predicate(mypred, name='foo')
        assert p.name == 'foo'
        assert p.num_args == 1
        assert p('a')

    def test_partial_function_predicate(self):
        def mypred(one, two, three):
            return one < two < three
        p = Predicate(functools.partial(mypred, 1))
        assert p.name == 'mypred'
        assert p.num_args == 2  # 3 - 1 partial
        assert p(2, 3)
        p = Predicate(functools.partial(mypred, 1, 2))
        assert p.name == 'mypred'
        assert p.num_args == 1  # 3 - 2 partial
        assert p(3)

    def test_method_predicate(self):
        class SomeClass(object):
            def some_method(self, arg1, arg2):
                return arg1 == arg2
        obj = SomeClass()
        p = Predicate(obj.some_method)
        assert p.name == 'some_method'
        assert p.num_args == 2
        assert p(2, 2)

    def test_partial_method_predicate(self):
        class SomeClass(object):
            def some_method(self, arg1, arg2):
                return arg1 == arg2
        obj = SomeClass()
        p = Predicate(functools.partial(obj.some_method, 2))
        assert p.name == 'some_method'
        assert p.num_args == 1
        assert p(2)

    def test_class_predicate(self):
        class callableclass(object):
            def __call__(self, arg1, arg2):
                return arg1 == arg2
        fn = callableclass()
        p = Predicate(fn)
        assert p.name == 'callableclass'
        assert p.num_args == 2
        assert p('a', 'a')

    def test_class_predicate_custom_name(self):
        class callableclass(object):
            def __call__(self, arg):
                return arg == 'a'
        fn = callableclass()
        p = Predicate(fn, name='bar')
        assert p.name == 'bar'
        assert p.num_args == 1
        assert p('a')

    def test_predicate_predicate(self):
        def mypred(x):
            return x == 'a'
        p = Predicate(Predicate(mypred))
        assert p.name == 'mypred'
        assert p.num_args == 1
        assert p('a')

    def test_predicate_predicate_custom_name(self):
        def mypred(x):
            return x == 'a'
        p = Predicate(Predicate(mypred, name='foo'))
        assert p.name == 'foo'
        assert p.num_args == 1
        assert p('a')

    def test_predicate_bind(self):
        @predicate(bind=True)
        def is_bound(self):
            return self is is_bound

        assert is_bound()

        p = None

        def mypred(self):
            return self is p

        p = Predicate(mypred, bind=True)
        assert p()

    def test_decorator(self):
        @predicate
        def mypred(arg1, arg2):
            return True
        assert mypred.name == 'mypred'
        assert mypred.num_args == 2

    def test_decorator_noargs(self):
        @predicate()
        def mypred(arg1, arg2):
            return True
        assert mypred.name == 'mypred'
        assert mypred.num_args == 2

    def test_decorator_custom_name(self):
        @predicate('foo')
        def mypred():
            return True
        assert mypred.name == 'foo'
        assert mypred.num_args == 0

        @predicate(name='bar')
        def myotherpred():
            return False
        assert myotherpred.name == 'bar'
        assert myotherpred.num_args == 0

    def test_repr(self):
        @predicate
        def mypred(arg1, arg2):
            return True
        assert repr(mypred).startswith('<Predicate:mypred object at 0x')

    def test_AND(self):
        p_AND1 = always_true & always_false
        assert not p_AND1()
        assert p_AND1.name == '(always_true & always_false)'
        p_AND2 = always_false & always_true
        assert not p_AND2()
        assert p_AND2.name == '(always_false & always_true)'
        p_AND3 = always_true & always_true
        assert p_AND3()
        assert p_AND3.name == '(always_true & always_true)'
        p_AND4 = always_false & always_false
        assert not p_AND4()
        assert p_AND4.name == '(always_false & always_false)'

    def test_OR(self):
        p_OR1 = always_true | always_false
        assert p_OR1()
        assert p_OR1.name == '(always_true | always_false)'
        p_OR2 = always_false | always_true
        assert p_OR2()
        assert p_OR2.name == '(always_false | always_true)'
        p_OR3 = always_true | always_true
        assert p_OR3()
        assert p_OR3.name == '(always_true | always_true)'
        p_OR4 = always_false | always_false
        assert not p_OR4()
        assert p_OR4.name == '(always_false | always_false)'

    def test_XOR(self):
        p_XOR1 = always_true ^ always_false
        assert p_XOR1()
        assert p_XOR1.name == '(always_true ^ always_false)'
        p_XOR2 = always_false ^ always_true
        assert p_XOR2()
        assert p_XOR2.name == '(always_false ^ always_true)'
        p_XOR3 = always_true ^ always_true
        assert not p_XOR3()
        assert p_XOR3.name == '(always_true ^ always_true)'
        p_XOR4 = always_false ^ always_false
        assert not p_XOR4()
        assert p_XOR4.name == '(always_false ^ always_false)'

    def test_INV(self):
        p_INV1 = ~always_true
        assert not p_INV1()
        assert p_INV1.name == '~always_true'
        p_INV2 = ~always_false
        assert p_INV2()
        assert p_INV2.name == '~always_false'
        p_INV3 = ~(~always_true)
        assert p_INV3()
        assert p_INV3.name == 'always_true'
        p_INV4 = ~(~always_false)
        assert not p_INV4()
        assert p_INV4.name == 'always_false'

    def test_var_args(self):
        @predicate
        def p(*args, **kwargs):
            assert len(args) > 0
            assert len(kwargs) == 0
        assert p.num_args == 0
        p.test('a')
        p.test('a', 'b')

    def test_no_args(self):
        @predicate
        def p(*args, **kwargs):
            assert len(args) == 0
            assert len(kwargs) == 0
        assert p.num_args == 0
        p.test()

    def test_one_arg(self):
        @predicate
        def p(a=None, *args, **kwargs):
            assert len(args) == 0
            assert len(kwargs) == 0
            assert a == 'a'
        assert p.num_args == 1
        p.test('a')

    def test_two_args(self):
        @predicate
        def p(a=None, b=None, *args, **kwargs):
            assert len(args) == 0
            assert len(kwargs) == 0
            assert a == 'a'
            assert b == 'b'
        assert p.num_args == 2
        p.test('a', 'b')

    def test_no_mask(self):
        @predicate
        def p(a=None, b=None, *args, **kwargs):
            assert len(args) == 0
            assert len(kwargs) == 1
            'c' in kwargs
            assert a == 'a'
            assert b == 'b'
        p('a', b='b', c='c')

    def test_no_value_marker(self):
        @predicate
        def p(a, b=None):
            assert a == 'a'
            assert b is None

        assert not NO_VALUE
        p.test('a')
        p.test('a', NO_VALUE)

    def test_short_circuit(self):
        @predicate
        def skipped_predicate(self):
            return None

        @predicate
        def shorted_predicate(self):
            raise Exception('this predicate should not be evaluated')

        assert (always_false & shorted_predicate).test() is False
        assert (always_true | shorted_predicate).test() is True

        def raises(pred):
            try:
                pred.test()
                return False
            except Exception as e:
                return 'evaluated' in str(e)

        assert raises(always_true & shorted_predicate)
        assert raises(always_false | shorted_predicate)
        assert raises(skipped_predicate & shorted_predicate)
        assert raises(skipped_predicate | shorted_predicate)

    def test_skip_predicate(self):
        @predicate(bind=True)
        def requires_two_args(self, a, b):
            return a == b if len(self.context.args) > 1 else None

        @predicate
        def passthrough(a):
            return a

        assert (requires_two_args & passthrough).test(True, True) is True
        assert (requires_two_args & passthrough).test(True, False) is False

        # because requires_two_args is called with only one argument
        # its result is not taken into account, only the result of the
        # other predicate matters.
        assert (requires_two_args & passthrough).test(True) is True
        assert (requires_two_args & passthrough).test(False) is False
        assert (requires_two_args | passthrough).test(True) is True
        assert (requires_two_args | passthrough).test(False) is False

        # test that order does not matter
        assert (passthrough & requires_two_args).test(True) is True
        assert (passthrough & requires_two_args).test(False) is False
        assert (passthrough | requires_two_args).test(True) is True
        assert (passthrough | requires_two_args).test(False) is False

        # test that inversion does not modify the result
        assert (~requires_two_args & passthrough).test(True) is True
        assert (~requires_two_args & passthrough).test(False) is False
        assert (~requires_two_args | passthrough).test(True) is True
        assert (~requires_two_args | passthrough).test(False) is False
        assert (passthrough & ~requires_two_args).test(True) is True
        assert (passthrough & ~requires_two_args).test(False) is False
        assert (passthrough | ~requires_two_args).test(True) is True
        assert (passthrough | ~requires_two_args).test(False) is False

        # test that when all predicates are skipped, result is False
        assert requires_two_args.test(True) is False
        assert (requires_two_args | requires_two_args).test(True) is False
        assert (requires_two_args & requires_two_args).test(True) is False

        # test that a skipped predicate doesn't alter the result at all
        assert (requires_two_args | requires_two_args | passthrough).test(True) is True
        assert (requires_two_args & requires_two_args & passthrough).test(True) is True

    def test_invocation_context(self):
        @predicate
        def p1():
            assert id(p1.context) == id(p2.context)
            assert p1.context.args == ('a',)
            return True

        @predicate
        def p2():
            assert id(p1.context) == id(p2.context)
            assert p2.context.args == ('a',)
            return True

        p = p1 & p2
        assert p.test('a')
        assert p.context is None

    def test_invocation_context_nested(self):
        @predicate
        def p1():
            assert p1.context.args == ('b1',)
            return True

        @predicate
        def p2():
            assert p2.context.args == ('b2',)
            return True

        @predicate
        def p():
            assert p1.context.args == ('a',)
            return p1.test('b1') & p2.test('b2')

        assert p.test('a')
        assert p.context is None

    def test_invocation_context_storage(self):
        @predicate
        def p1(a):
            p1.context['p1.a'] = a
            return True

        @predicate
        def p2(a):
            return p2.context['p1.a'] == a

        p = p1 & p2
        assert p.test('a')
