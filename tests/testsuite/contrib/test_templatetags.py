from django.contrib.auth.models import User
from django.template import Template, Context
from django.test import TestCase

from testapp.models import Book

from . import ISBN, TestData


class TemplateTagTests(TestData, TestCase):
    tpl_format = """{{% spaceless %}}
        {{% load rules %}}
        {{% {tag} "{name}" user book as can_update %}}
        {{% if can_update %}}
        OK
        {{% else %}}
        NOT OK
        {{% endif %}}
        {{% endspaceless %}}"""

    def test_rule_tag(self):

        # change_book rule

        tpl = Template(self.tpl_format.format(tag='test_rule', name='change_book'))

        # adrian can change his book as its author
        html = tpl.render(Context({
            'user': User.objects.get(username='adrian'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'OK')

        # martin can change adrian's book as an editor
        html = tpl.render(Context({
            'user': User.objects.get(username='martin'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'OK')

        # delete_book rule

        tpl = Template(self.tpl_format.format(tag='test_rule', name='delete_book'))

        # adrian can delete his book as its author
        html = tpl.render(Context({
            'user': User.objects.get(username='adrian'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'OK')

        # martin can *not* delete adrian's book
        html = tpl.render(Context({
            'user': User.objects.get(username='martin'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'NOT OK')

    def test_perm_tag(self):

        # change_book permission

        tpl = Template(self.tpl_format.format(tag='has_perm', name='testapp.change_book'))

        # adrian can change his book as its author
        html = tpl.render(Context({
            'user': User.objects.get(username='adrian'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'OK')

        # martin can change adrian's book as an editor
        html = tpl.render(Context({
            'user': User.objects.get(username='martin'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'OK')

        # delete_book permission

        tpl = Template(self.tpl_format.format(tag='has_perm', name='testapp.delete_book'))

        # adrian can delete his book as its author
        html = tpl.render(Context({
            'user': User.objects.get(username='adrian'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'OK')

        # martin can *not* delete adrian's book
        html = tpl.render(Context({
            'user': User.objects.get(username='martin'),
            'book': Book.objects.get(isbn=ISBN),
        }))
        self.assertEqual(html, 'NOT OK')
