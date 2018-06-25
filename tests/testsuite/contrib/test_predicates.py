from django.contrib.auth.models import User
from django.test import TestCase

from rules.predicates import (is_authenticated, is_superuser, is_staff,
                              is_active, is_group_member)

from . import TestData


class SwappedUser(object):
    pass


class PredicateTests(TestData, TestCase):
    def test_is_authenticated(self):
        assert is_authenticated(User.objects.get(username='adrian'))
        assert not is_authenticated(SwappedUser())

    def test_is_superuser(self):
        assert is_superuser(User.objects.get(username='adrian'))
        assert not is_superuser(SwappedUser())

    def test_is_staff(self):
        assert is_staff(User.objects.get(username='adrian'))
        assert not is_staff(SwappedUser())

    def test_is_active(self):
        assert is_active(User.objects.get(username='adrian'))
        assert not is_active(SwappedUser())

    def test_is_group_member(self):
        p1 = is_group_member('somegroup')
        assert p1.name == 'is_group_member:somegroup'
        assert p1.num_args == 1

        p2 = is_group_member('g1', 'g2', 'g3', 'g4')
        assert p2.name == 'is_group_member:g1,g2,g3,...'

        p = is_group_member('editors')
        assert p(User.objects.get(username='martin'))
        assert not p(SwappedUser())

        p = is_group_member('editors', 'staff')
        assert not p(User.objects.get(username='martin'))
        assert not p(SwappedUser())
