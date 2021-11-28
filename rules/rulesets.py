from .predicates import predicate


class RuleSet(dict):
    def test_rule(self, name, *args, **kwargs):
        return name in self and self[name]['pred'].test(*args, **kwargs)

    def rule_exists(self, name):
        return name in self

    def rule_verbose_name(self, name):
        return self[name]['verbose_name'] or name

    def add_rule(self, name, pred, verbose_name=None):
        if name in self:
            raise KeyError("A rule with name `%s` already exists" % name)

        self[name] = {'pred': predicate(pred), 'verbose_name': verbose_name}

    def set_rule(self, name, pred, verbose_name=None):
        self[name] = {'pred': pred, 'verbose_name': verbose_name}

    def remove_rule(self, name):
        del self[name]

    def __setitem__(self, name, pred_dict):
        super(RuleSet, self).__setitem__(name, pred_dict)


# Shared rule set

default_rules = RuleSet()


def add_rule(name, pred, verbose_name=None):
    default_rules.add_rule(name, pred, verbose_name=verbose_name)

def set_rule(name, pred, verbose_name=None):
    default_rules.set_rule(name, pred, verbose_name=verbose_name)

def remove_rule(name):
    default_rules.remove_rule(name)

def rule_exists(name):
    return default_rules.rule_exists(name)

def rule_verbose_name(name):
    return default_rules.rule_verbose_name(name)

def test_rule(name, *args, **kwargs):
    return default_rules.test_rule(name, *args, **kwargs)
