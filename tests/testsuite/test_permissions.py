from unittest import TestCase

from rules.permissions import (
    ObjectPermissionBackend,
    add_perm,
    has_perm,
    perm_exists,
    perm_verbose_name,
    permissions,
    remove_perm,
    set_perm,
)
from rules.predicates import always_false, always_true


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
        add_perm("can_edit_book", always_true)
        assert "can_edit_book" in permissions
        assert perm_exists("can_edit_book")
        assert has_perm("can_edit_book")
        with self.assertRaises(KeyError):
            add_perm("can_edit_book", always_false)
        set_perm("can_edit_book", always_false)
        assert not has_perm("can_edit_book")
        remove_perm("can_edit_book")
        assert not perm_exists("can_edit_book")

    def test_permissions_verbose_name(self):
        perm_name = "can_shred_book"
        add_perm(perm_name, always_true, verbose_name="Can this user shred book?")
        assert perm_exists(perm_name)
        assert "Can this user shred book?" in perm_verbose_name(perm_name)
        assert has_perm(perm_name)
        with self.assertRaises(KeyError):
            add_perm(perm_name, always_false)
        set_perm(perm_name, always_false, verbose_name="User cannot shred book!")
        assert "User cannot shred book!" in perm_verbose_name(perm_name)
        assert not has_perm(perm_name)
        remove_perm(perm_name)
        assert not perm_exists(perm_name)

    def test_backend(self):
        backend = ObjectPermissionBackend()
        assert backend.authenticate("someuser", "password") is None

        add_perm("can_edit_book", always_true)
        assert "can_edit_book" in permissions
        assert backend.has_perm(None, "can_edit_book")
        assert backend.has_module_perms(None, "can_edit_book")
        with self.assertRaises(KeyError):
            add_perm("can_edit_book", always_true)
        set_perm("can_edit_book", always_false)
        assert not backend.has_perm(None, "can_edit_book")
        remove_perm("can_edit_book")
        assert not perm_exists("can_edit_book")
