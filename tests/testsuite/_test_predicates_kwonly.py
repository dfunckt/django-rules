from unittest import TestCase

from rules.predicates import predicate


class PredicateKwonlyTests(TestCase):
    def test_predicate_kwargonly(self):
        def p(foo, *, bar):
            return True
        with self.assertRaises(TypeError):
            predicate(p)

        def p2(foo, *a, bar):
            return True
        with self.assertRaises(TypeError):
            predicate(p2)

        def p3(foo, *, bar='bar'):
            return True
        # Should not fail
        predicate(p3)
