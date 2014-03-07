from .rulesets import RuleSet


permissions = RuleSet()


def add_perm(name, pred):
    permissions.add_rule(name, pred)


def remove_perm(name):
    permissions.remove_rule(name)


def perm_exists(name):
    return permissions.rule_exists(name)


def has_perm(name, obj=None, target=None):
    return permissions.test_rule(name, obj, target)


class ObjectPermissionBackend(object):
    def authenticate(self, username, password):
        return None
    
    def has_perm(self, user, perm, obj=None):
        return has_perm(perm, user, obj)
