from django import template

from ..rulesets import default_rules


register = template.Library()
register_tag = register.assignment_tag if hasattr(register, 'assignment_tag') else register.simple_tag


@register_tag
def test_rule(name, obj=None, target=None):
    return default_rules.test_rule(name, obj, target)


@register_tag
def has_perm(perm, user, obj=None):
    if not hasattr(user, 'has_perm'):  # pragma: no cover
        return False  # swapped user model that doesn't support permissions
    else:
        return user.has_perm(perm, obj)
