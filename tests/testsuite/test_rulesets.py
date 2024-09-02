from unittest import TestCase

from rules.predicates import always_false, always_true
from rules.rulesets import (
    RuleSet,
    add_rule,
    default_rules,
    remove_rule,
    rule_exists,
    rule_verbose_name,
    set_rule,
    test_rule,
)


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
        add_rule("somerule", always_true)
        assert "somerule" in default_rules
        assert rule_exists("somerule")
        assert test_rule("somerule")
        assert test_rule("somerule")
        with self.assertRaises(KeyError):
            add_rule("somerule", always_false)
        set_rule("somerule", always_false)
        assert not test_rule("somerule")
        remove_rule("somerule")
        assert not rule_exists("somerule")

    def test_shared_ruleset_verbose(self):
        add_rule("somerule", always_true, verbose_name="Some Rule which is always true")
        assert "somerule" in default_rules
        assert rule_exists("somerule")
        assert test_rule("somerule")
        assert "Some Rule which is always true" in rule_verbose_name("somerule")
        with self.assertRaises(KeyError):
            add_rule("somerule", always_false)
        set_rule("somerule", always_false)
        assert not test_rule("somerule")
        remove_rule("somerule")
        assert not rule_exists("somerule")

    def test_ruleset(self):
        ruleset = RuleSet()
        ruleset.add_rule("somerule", always_true)
        assert "somerule" in ruleset
        assert ruleset.rule_exists("somerule")
        assert ruleset.test_rule("somerule")
        with self.assertRaises(KeyError):
            ruleset.add_rule("somerule", always_true)
        ruleset.set_rule("somerule", always_false)
        assert not test_rule("somerule")
        ruleset.remove_rule("somerule")
        assert not ruleset.rule_exists("somerule")

    def test_ruleset_verbose(self):
        ruleset = RuleSet()
        ruleset.add_rule("somerule", always_true, verbose_name="Some Rule which is always true")
        assert "somerule" in ruleset
        assert ruleset.rule_exists("somerule")
        assert ruleset.test_rule("somerule")
        assert "Some Rule which is always true" in ruleset.rule_verbose_name("somerule")
        with self.assertRaises(KeyError):
            ruleset.add_rule("somerule", always_true)
        ruleset.set_rule("somerule", always_false)
        assert not test_rule("somerule")
        ruleset.remove_rule("somerule")
        assert not ruleset.rule_exists("somerule")
