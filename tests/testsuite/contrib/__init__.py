from django.contrib.auth.models import Group, User

import testapp.rules  # noqa .imported to register rules
from testapp.models import Book

ISBN = "978-1-4302-1936-1"


class TestData:
    @classmethod
    def setUpTestData(cls):
        adrian = User.objects.create_user(
            "adrian", password="secr3t", is_superuser=True, is_staff=True
        )

        martin = User.objects.create_user("martin", password="secr3t", is_staff=True)

        editors = Group.objects.create(name="editors")
        martin.groups.add(editors)

        Book.objects.create(
            isbn=ISBN, title="The Definitive Guide to Django", author=adrian
        )
