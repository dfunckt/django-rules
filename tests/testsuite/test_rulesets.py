from nose.tools import nottest, with_setup, assert_raises

from rules.predicates import predicate, NOT_GIVEN
from rules.rulesets import (RuleSet, default_rules, add_rule, remove_rule,
                            rule_exists, test_rule)


test_rule = nottest(test_rule)


def reset_ruleset(ruleset):
    def fn():
        for k in list(ruleset.keys()):
            ruleset.pop(k)
    return fn


@predicate
def always_true():
    return True


@predicate
def expect_two_args(a, b):
    assert a is not NOT_GIVEN
    assert b is not NOT_GIVEN
    return True


@predicate
def expect_one_arg(a, b):
    assert a is not NOT_GIVEN
    assert b is NOT_GIVEN
    return True


@predicate
def expect_no_arg(a, b):
    assert a is NOT_GIVEN
    assert b is NOT_GIVEN
    return True


@with_setup(reset_ruleset(default_rules), reset_ruleset(default_rules))
def test_shared_ruleset():
    add_rule('somerule', always_true)
    assert 'somerule' in default_rules
    assert rule_exists('somerule')
    assert test_rule('somerule')
    remove_rule('somerule')
    assert not rule_exists('somerule')


def test_ruleset():
    ruleset = RuleSet()
    ruleset.add_rule('somerule', always_true)
    assert 'somerule' in ruleset
    assert ruleset.rule_exists('somerule')
    assert ruleset.test_rule('somerule')
    assert_raises(KeyError, ruleset.add_rule, 'somerule', always_true)
    ruleset.remove_rule('somerule')
    assert not ruleset.rule_exists('somerule')


def test_not_given_argument():
    ruleset = RuleSet()
    ruleset.add_rule('two_args', expect_two_args)
    ruleset.add_rule('one_arg', expect_one_arg)
    ruleset.add_rule('no_arg', expect_no_arg)

    assert ruleset.test_rule('two_args', 'a', 'a')
    assert_raises(AssertionError, ruleset.test_rule, 'two_args', 'a')
    assert_raises(AssertionError, ruleset.test_rule, 'two_args')
    assert ruleset.test_rule('one_arg', 'a')
    assert_raises(AssertionError, ruleset.test_rule, 'one_arg')
    assert ruleset.test_rule('no_arg')
    assert_raises(AssertionError, ruleset.test_rule, 'no_arg', 'a', 'b')
