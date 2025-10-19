from .rulesets import RuleSet

permissions = RuleSet()


def add_perm(name, pred, verbose_name=None):
    permissions.add_rule(name, pred, verbose_name=verbose_name)


def set_perm(name, pred, verbose_name=None):
    permissions.set_rule(name, pred, verbose_name=verbose_name)


def remove_perm(name):
    permissions.remove_rule(name)


def perm_exists(name):
    return permissions.rule_exists(name)


def perm_verbose_name(name):
    return permissions.rule_verbose_name(name)


def has_perm(name, *args, **kwargs):
    return permissions.test_rule(name, *args, **kwargs)


class ObjectPermissionBackend(object):
    def authenticate(self, *args, **kwargs):
        return None

    def has_perm(self, user, perm, *args, **kwargs):
        return has_perm(perm, user, *args, **kwargs)

    def has_module_perms(self, user, app_label):
        return has_perm(app_label, user)
