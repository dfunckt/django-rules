from unittest import TestCase

from rules.predicates import always_true, always_false
from rules.permissions import (permissions, add_perm, set_perm, remove_perm,
                               perm_exists, has_perm, ObjectPermissionBackend)


class PermissionsTests(TestCase):
    @staticmethod
    def reset_ruleset(ruleset):
        for k in list(ruleset.keys()):
            ruleset.pop(k)

    def setUp(self):
        self.reset_ruleset(permissions)

    def tearDown(self):
        self.reset_ruleset(permissions)

    def test_permissions_ruleset(self):
        add_perm('can_edit_book', always_true)
        assert 'can_edit_book' in permissions
        assert perm_exists('can_edit_book')
        assert has_perm('can_edit_book')
        with self.assertRaises(KeyError):
            add_perm('can_edit_book', always_false)
        set_perm('can_edit_book', always_false)
        assert not has_perm('can_edit_book')
        remove_perm('can_edit_book')
        assert not perm_exists('can_edit_book')

    def test_backend(self):
        backend = ObjectPermissionBackend()
        assert backend.authenticate('someuser', 'password') is None

        add_perm('can_edit_book', always_true)
        assert 'can_edit_book' in permissions
        assert backend.has_perm(None, 'can_edit_book')
        assert backend.has_module_perms(None, 'can_edit_book')
        with self.assertRaises(KeyError):
            add_perm('can_edit_book', always_true)
        set_perm('can_edit_book', always_false)
        assert not backend.has_perm(None, 'can_edit_book')
        remove_perm('can_edit_book')
        assert not perm_exists('can_edit_book')
