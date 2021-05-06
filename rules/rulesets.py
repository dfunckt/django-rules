from .predicates import predicate


class RuleSet(dict):
    def test_rule(self, name, *args, **kwargs):
        return name in self and self[name].test(*args, **kwargs)

    def rule_exists(self, name):
        return name in self

    def add_rule(self, name, pred):
        if name in self:
            raise KeyError("A rule with name `%s` already exists" % name)
        self[name] = pred

    def set_rule(self, name, pred):
        self[name] = pred

    def remove_rule(self, name):
        del self[name]

    def __setitem__(self, name, pred):
        fn = predicate(pred)
        super(RuleSet, self).__setitem__(name, fn)


# Shared rule set

default_rules = RuleSet()


def add_rule(name, pred):
    default_rules.add_rule(name, pred)


def set_rule(name, pred):
    default_rules.set_rule(name, pred)


def remove_rule(name):
    default_rules.remove_rule(name)


def rule_exists(name):
    return default_rules.rule_exists(name)


def test_rule(name, *args, **kwargs):
    return default_rules.test_rule(name, *args, **kwargs)
