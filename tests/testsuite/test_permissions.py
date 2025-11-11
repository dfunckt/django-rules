from unittest import TestCase

from asgiref.sync import sync_to_async

from rules.permissions import (
    ObjectPermissionBackend,
    add_perm,
    has_perm,
    perm_exists,
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

    async def test_backend_async(self):
        backend = ObjectPermissionBackend()

        await sync_to_async(add_perm)("can_edit_book", always_true)
        assert "can_edit_book" in permissions
        assert await backend.ahas_perm(None, "can_edit_book")
        assert await backend.ahas_module_perms(None, "can_edit_book")
        with self.assertRaises(KeyError):
            await sync_to_async(add_perm)("can_edit_book", always_true)
        await sync_to_async(set_perm)("can_edit_book", always_false)
        assert not await backend.ahas_perm(None, "can_edit_book")
        await sync_to_async(remove_perm)("can_edit_book")
        assert not await sync_to_async(perm_exists)("can_edit_book")
