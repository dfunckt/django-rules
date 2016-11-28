from django.contrib.auth.models import User, Group
from testapp.models import Book

import testapp.rules  # to register rules


ISBN = '978-1-4302-1936-1'


def setup_package():
    adrian = User.objects.create_user('adrian', password='secr3t')
    adrian.is_superuser = True
    adrian.is_staff = True
    adrian.save()

    martin = User.objects.create_user('martin', password='secr3t')
    martin.is_staff = True
    martin.save()

    editors = Group.objects.create(name='editors')
    martin.groups.add(editors)

    Book.objects.create(
        isbn=ISBN,
        title='The Definitive Guide to Django',
        author=adrian)


def teardown_package():
    Book.objects.get(isbn=ISBN).delete()
    Group.objects.get(name='editors').delete()
    User.objects.get(username='adrian').delete()
    User.objects.get(username='martin').delete()
