from unittest import TestCase

from rules.predicates import always_true, always_false
from rules.rulesets import (RuleSet, default_rules, add_rule, remove_rule,
                            replace_rule, rule_exists, test_rule)


class RulesetTests(TestCase):
    @staticmethod
    def reset_ruleset(ruleset):
        for k in list(ruleset.keys()):
            ruleset.pop(k)

    def setUp(self):
        self.reset_ruleset(default_rules)

    def tearDown(self):
        self.reset_ruleset(default_rules)

    def test_shared_ruleset(self):
        add_rule('somerule', always_true)
        assert 'somerule' in default_rules
        assert rule_exists('somerule')
        assert test_rule('somerule')
        assert test_rule('somerule')
        with self.assertRaises(KeyError):
            add_rule('somerule', always_false)
        replace_rule('somerule', always_false)
        assert not test_rule('somerule')
        with self.assertRaises(KeyError):
            replace_rule('someotherrule', always_false)
        remove_rule('somerule')
        assert not rule_exists('somerule')

    def test_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule('somerule', always_true)
        assert 'somerule' in ruleset
        assert ruleset.rule_exists('somerule')
        assert ruleset.test_rule('somerule')
        with self.assertRaises(KeyError):
            ruleset.add_rule('somerule', always_true)
        ruleset.replace_rule('somerule', always_false)
        assert not test_rule('somerule')
        with self.assertRaises(KeyError):
            ruleset.replace_rule('someotherrule', always_false)
        ruleset.remove_rule('somerule')
        assert not ruleset.rule_exists('somerule')
