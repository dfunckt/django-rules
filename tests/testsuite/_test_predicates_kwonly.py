from nose.tools import assert_raises
from functools import partial

from rules.predicates import predicate


def test_predicate_kwargonly():
    def p(foo, *, bar):
        return True
    assert_raises(TypeError, predicate, p)

    def p2(foo, *a, bar):
        return True
    assert_raises(TypeError, predicate, p2)

    def p3(foo, *, bar='bar'):
        return True
    # Should not fail
    predicate(p3)
