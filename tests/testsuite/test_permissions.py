from nose.tools import with_setup, assert_raises

from rules.predicates import always_true, always_false
from rules.permissions import (permissions, add_perm, replace_perm, remove_perm,
                               perm_exists, has_perm, ObjectPermissionBackend)


def reset_ruleset(ruleset):
    def fn():
        for k in list(ruleset.keys()):
            ruleset.pop(k)
    return fn


@with_setup(reset_ruleset(permissions), reset_ruleset(permissions))
def test_permissions_ruleset():
    add_perm('can_edit_book', always_true)
    assert 'can_edit_book' in permissions
    assert perm_exists('can_edit_book')
    assert has_perm('can_edit_book')
    replace_perm('can_edit_book', always_false)
    assert not has_perm('can_edit_book')
    assert_raises(KeyError, replace_perm, 'someotherperm', always_false)
    remove_perm('can_edit_book')
    assert not perm_exists('can_edit_book')


@with_setup(reset_ruleset(permissions), reset_ruleset(permissions))
def test_backend():
    backend = ObjectPermissionBackend()
    assert backend.authenticate('someuser', 'password') is None

    add_perm('can_edit_book', always_true)
    assert 'can_edit_book' in permissions
    assert backend.has_perm(None, 'can_edit_book')
    assert backend.has_module_perms(None, 'can_edit_book')
    assert_raises(KeyError, add_perm, 'can_edit_book', always_true)
    replace_perm('can_edit_book', always_false)
    assert not backend.has_perm(None, 'can_edit_book')
    assert_raises(KeyError, replace_perm, 'someotherperm', always_false)
    remove_perm('can_edit_book')
    assert not perm_exists('can_edit_book')
