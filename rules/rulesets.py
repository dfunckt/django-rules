from .predicates import predicate, Predicate
from inspect import isfunction


class RuleSet(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def test_rule(self, name, *args, **kwargs):
        # return name in self and self[name]['pred'].test(*args, **kwargs)
        return name in self and self[name].test(*args, **kwargs)

    def rule_exists(self, name):
        return name in self

    def rule_verbose_name(self, name):
        return self["get_%s_display" % name] or name

    def add_rule(self, name, pred, verbose_name=None):
        if name in self:
            raise KeyError("A rule with name `%s` already exists" % name)

        self[name] = {'pred': predicate(pred), 'verbose_name': verbose_name}

    def set_rule(self, name, pred, verbose_name=None):
        self[name] = {'pred': predicate(pred), 'verbose_name': verbose_name}

    def remove_rule(self, name):
        del self[name]

    def __setitem__(self, name, pred):
        if isfunction(pred):
            # If a function as passed in (as might be done with legacy django-rules)
            #   convert the value to the dictionary form
            pred = {'pred': predicate(pred), 'verbose_name': verbose_name}

        if isinstance(pred, dict):
            # Check if internal pred is already a Predicate, or an basic
            #   unwrapped function. Wrap as a Predicate if needed
            if not isinstance(pred['pred'], Predicate):
                pred['pred'] = predicate(pred['pred'])

        super(RuleSet, self).__setitem__(name, pred)

    def __getitem__(self, name):
        def _check_name(_name):
            if (not super(RuleSet, self).__contains__(_name)):
                raise KeyError("Provided name '`%s`' not found" % _name)

        if name[0] != '_':
            prefix = "get_"
            suffix = "_display"
            if name.startswith(prefix) and name.endswith(suffix):
                _name = name[len(prefix):-len(suffix)]
                _check_name(_name)
                return super(RuleSet, self).__getitem__(_name)['verbose_name']

            _check_name(name)            
        return super().__getitem__(name)['pred']
        
    def __iter__(self):
        for name in range(len(self)):
            yield self[name]

    def __reversed__(self):
        for name in reversed(range(len(self))):
            yield self[name]

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
