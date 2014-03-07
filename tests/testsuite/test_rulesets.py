from nose.tools import nottest, with_setup, assert_raises

from rules.predicates import predicate
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
