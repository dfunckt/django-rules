from nose.tools import assert_raises

from rules.predicates import Predicate, predicate, NOT_GIVEN


def test_lambda_predicate():
    p = Predicate(lambda: True)
    assert p.name == '<lambda>'
    assert p.num_args == 0


def test_lambda_predicate_custom_name():
    p = Predicate(lambda: True, name='always_true')
    assert p.name == 'always_true'


def test_function_predicate():
    def always_true():
        return True
    p = Predicate(always_true)
    assert p.name == 'always_true'
    assert p.num_args == 0


def test_function_predicate_custom_name():
    def always_true():
        return True
    p = Predicate(always_true, name='foo')
    assert p.name == 'foo'
    assert p.num_args == 0


def test_class_predicate():
    class callableclass(object):
        def __call__(self, arg1, arg2):
            return True
    fn = callableclass()
    p = Predicate(fn)
    assert p.name == 'callableclass'
    assert p.num_args == 2


def test_class_predicate_custom_name():
    class callableclass(object):
        def __call__(self, arg):
            return True
    fn = callableclass()
    p = Predicate(fn, name='bar')
    assert p.name == 'bar'
    assert p.num_args == 1


def test_predicate_predicate():
    def always_true():
        return True
    p = Predicate(Predicate(always_true))
    assert p.name == 'always_true'
    assert p.num_args == 0


def test_predicate_predicate_custom_name():
    def always_true():
        return True
    p = Predicate(Predicate(always_true, name='foo'))
    assert p.name == 'foo'
    assert p.num_args == 0


def test_decorator():
    @predicate
    def always_true(arg1, arg2):
        return True
    assert always_true.name == 'always_true'
    assert always_true.num_args == 2


def test_decorator_noargs():
    @predicate()
    def always_true(arg1, arg2):
        return True
    assert always_true.name == 'always_true'
    assert always_true.num_args == 2


def test_decorator_custom_name():
    @predicate('foo')
    def always_true():
        return True
    assert always_true.name == 'foo'
    assert always_true.num_args == 0

    @predicate(name='bar')
    def always_false():
        return False
    assert always_false.name == 'bar'
    assert always_false.num_args == 0


def test_repr():
    @predicate
    def always_true(arg1, arg2):
        return True
    assert repr(always_true).startswith('<Predicate:always_true object at 0x')


@predicate
def always_true():
    return True


@predicate
def always_false():
    return False


def test_AND():
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


def test_OR():
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


def test_XOR():
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


def test_INV():
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


def test_var_args():
    @predicate
    def p(*args, **kwargs):
        assert len(args) == 0
        assert len(kwargs) == 0
    assert p.num_args == 0
    p.test()
    p.test('a')
    p.test('a', 'b')


def test_no_args():
    @predicate
    def p(*args, **kwargs):
        assert len(args) == 0
        assert len(kwargs) == 0
    assert p.num_args == 0
    p.test()


def test_one_arg():
    @predicate
    def p(a=None, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs) == 0
        assert a == 'a'
    assert p.num_args == 1
    p.test('a')


def test_two_args():
    @predicate
    def p(a=None, b=None, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs) == 0
        assert a == 'a'
        assert b == 'b'
    assert p.num_args == 2
    p.test('a', 'b')


def test_no_mask():
    @predicate
    def p(a=None, b=None, *args, **kwargs):
        assert len(args) == 0
        assert len(kwargs) == 1
        'c' in kwargs
        assert a == 'a'
        assert b == 'b'
    p('a', b='b', c='c')


def test_positional_args_not_given():
    @predicate
    def p(a, b):
        if b is NOT_GIVEN:
            assert a == 'a'
        elif a is NOT_GIVEN:
            raise TypeError
        else:
            assert a == b

    p('a', NOT_GIVEN)
    p('a', 'a')
    assert not NOT_GIVEN
    assert_raises(TypeError, p)
    assert_raises(AssertionError, p, 'a', 'b')
