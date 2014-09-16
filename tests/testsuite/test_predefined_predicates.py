from rules.predicates import (always_true, always_false, always_allow,
                              always_deny, is_authenticated, is_superuser,
                              is_staff, is_active, is_group_member)


# mock models

class User(object):
    is_superuser = True
    is_staff = True
    is_active = True

    _group_names_cache = set(['editors'])
    groups = ['editors']

    def is_authenticated(self):
        return True


class SwappedUser(object):
    pass


def test_always_true():
    assert always_true()


def test_always_false():
    assert not always_false()


def test_always_allow():
    assert always_allow()


def test_always_deny():
    assert not always_deny()


def test_is_authenticated():
    assert is_authenticated(User())
    assert not is_authenticated(SwappedUser())


def test_is_superuser():
    assert is_superuser(User())
    assert not is_superuser(SwappedUser())


def test_is_staff():
    assert is_staff(User())
    assert not is_staff(SwappedUser())


def test_is_active():
    assert is_active(User())
    assert not is_active(SwappedUser())


def test_is_group_member():
    p1 = is_group_member('somegroup')
    assert p1.name == 'is_group_member:somegroup'
    assert p1.num_args == 1

    p2 = is_group_member('g1', 'g2', 'g3', 'g4')
    assert p2.name == 'is_group_member:g1,g2,g3,...'

    p = is_group_member('editors')
    assert p(User())
    assert not p(SwappedUser())

    p = is_group_member('editors', 'staff')
    assert not p(User())
    assert not p(SwappedUser())
