from .rulesets import RuleSet

permissions = RuleSet()


async def _run_async(func, *args, **kwargs):
    from asgiref.sync import sync_to_async

    return await sync_to_async(func)(*args, **kwargs)


def add_perm(name, pred):
    permissions.add_rule(name, pred)


def set_perm(name, pred):
    permissions.set_rule(name, pred)


def remove_perm(name):
    permissions.remove_rule(name)


def perm_exists(name):
    return permissions.rule_exists(name)


def has_perm(name, *args, **kwargs):
    return permissions.test_rule(name, *args, **kwargs)


class ObjectPermissionBackend(object):
    def authenticate(self, *args, **kwargs):
        return None

    def has_perm(self, user, perm, *args, **kwargs):
        return has_perm(perm, user, *args, **kwargs)

    def has_module_perms(self, user, app_label):
        return has_perm(app_label, user)

    async def aauthenticate(self, *args, **kwargs):
        return None

    async def ahas_perm(self, user, perm, *args, **kwargs):
        return await _run_async(has_perm, user, perm, *args, **kwargs)

    async def ahas_module_perms(self, user, app_label):
        return await _run_async(has_perm, app_label, user)
