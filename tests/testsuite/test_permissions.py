from nose.tools import with_setup, assert_raises

from rules.predicates import predicate, NOT_GIVEN
from rules.permissions import (permissions, add_perm, remove_perm,
                               perm_exists, has_perm, ObjectPermissionBackend)


def reset_ruleset(ruleset):
    def fn():
        for k in list(ruleset.keys()):
            ruleset.pop(k)
    return fn


@predicate
def always_true():
    return True


@predicate
def expect_two_args(user, perm):
    assert user is not NOT_GIVEN
    assert perm is not NOT_GIVEN
    return True


@predicate
def expect_one_arg(user, perm):
    assert user is not NOT_GIVEN
    assert perm is NOT_GIVEN
    return True


@predicate
def expect_no_arg(user, perm):
    assert user is NOT_GIVEN
    assert perm is NOT_GIVEN
    return True


@with_setup(reset_ruleset(permissions), reset_ruleset(permissions))
def test_permissions_ruleset():
    add_perm('can_edit_book', always_true)
    assert 'can_edit_book' in permissions
    assert perm_exists('can_edit_book')
    assert has_perm('can_edit_book')
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
    remove_perm('can_edit_book')
    assert not perm_exists('can_edit_book')


@with_setup(reset_ruleset(permissions), reset_ruleset(permissions))
def test_backend_with_not_given():
    backend = ObjectPermissionBackend()
    user = object()
    obj= object()

    add_perm('can_edit_book_2', expect_two_args)
    add_perm('can_edit_book_1', expect_one_arg)
    assert 'can_edit_book_2' in permissions
    assert 'can_edit_book_1' in permissions
    assert backend.has_perm(user, 'can_edit_book_2', obj)
    assert backend.has_perm(user, 'can_edit_book_1')
    assert_raises(AssertionError, backend.has_perm, user, 'can_edit_book_2')


def test_not_given_argument():
    add_perm('two_args', expect_two_args)
    add_perm('one_arg', expect_one_arg)
    add_perm('no_arg', expect_no_arg)

    assert has_perm('two_args', 'a', 'a')
    assert_raises(AssertionError, has_perm, 'two_args', 'a')
    assert_raises(AssertionError, has_perm, 'two_args')
    assert has_perm('one_arg', 'a')
    assert_raises(AssertionError, has_perm, 'one_arg')
    assert has_perm('no_arg')
    assert_raises(AssertionError, has_perm, 'no_arg', 'a', 'b')
