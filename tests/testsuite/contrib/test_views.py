from __future__ import absolute_import

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404, HttpRequest
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.encoding import force_str
from django.views.generic import CreateView, View

from testapp.models import Book

import rules  # noqa
from rules.contrib.views import AutoPermissionRequiredMixin, objectgetter

from . import TestData


class FBVDecoratorTests(TestData, TestCase):
    def test_objectgetter(self):
        request = HttpRequest()
        book = Book.objects.get(pk=1)

        self.assertEqual(book, objectgetter(Book)(request, pk=1))
        self.assertEqual(book, objectgetter(Book, attr_name="id")(request, id=1))
        self.assertEqual(book, objectgetter(Book, field_name="id")(request, pk=1))

        with self.assertRaises(ImproperlyConfigured):
            # Raise if no `pk` argument is provided to the view
            self.assertEqual(book, objectgetter(Book)(request, foo=1))

        with self.assertRaises(ImproperlyConfigured):
            # Raise if given invalid model lookup field
            self.assertEqual(book, objectgetter(Book, field_name="foo")(request, pk=1))

        with self.assertRaises(Http404):
            # Raise 404 if no model instance found
            self.assertEqual(book, objectgetter(Book)(request, pk=100000))

    def test_permission_required(self):
        # Adrian can change his book
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("change_book", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Martin can change Adrian's book
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("change_book", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Adrian can delete his book
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("delete_book", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Martin can *not* create a book
        # Up to Django v2.1, the response was a redirect to login
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("cbv.create_book"))
        self.assertIn(response.status_code, [302, 403])

        # Martin can *not* delete Adrian's book and is redirected to login
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("delete_book", args=(1,)))
        self.assertEqual(response.status_code, 302)

        # Martin can *not* delete Adrian's book and an PermissionDenied is raised
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("view_that_raises", args=(1,)))
        self.assertEqual(response.status_code, 403)

        # Test views that require a list of permissions

        # Adrian has both permissions
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("view_with_permission_list", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Martin does not have delete permission
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("view_with_permission_list", args=(1,)))
        self.assertEqual(response.status_code, 302)

        # Test views that accept a static object as argument
        # fn is passed to has_perm as-is

        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("view_with_object", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("view_with_object", args=(1,)))
        self.assertEqual(response.status_code, 302)


class CBVMixinTests(TestData, TestCase):
    def test_get_object_error(self):
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        with self.assertRaises(AttributeError):
            self.client.get(reverse("cbv.change_book_error", args=(1,)))

    def test_permission_required_mixin(self):
        # Adrian can change his book
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("cbv.change_book", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Martin can change Adrian's book
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("cbv.change_book", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Adrian can delete his book
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("cbv.delete_book", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Martin can *not* delete Adrian's book
        # Up to Django v2.1, the response was a redirect to login
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("cbv.delete_book", args=(1,)))
        self.assertIn(response.status_code, [302, 403])

        # Martin can *not* delete Adrian's book and an PermissionDenied is raised
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("cbv.view_that_raises", args=(1,)))
        self.assertEqual(response.status_code, 403)

        # Test views that require a list of permissions

        # Adrian has both permissions
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("cbv.view_with_permission_list", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content).strip(), "OK")

        # Martin does not have delete permission
        # Up to Django v2.1, the response was a redirect to login
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("cbv.view_with_permission_list", args=(1,)))
        self.assertIn(response.status_code, [302, 403])


class AutoPermissionRequiredMixinTests(TestCase):
    def setUp(self):
        from testapp.models import TestModel

        self.model = TestModel
        self.req = RequestFactory().get("/")
        self.req.user = AnonymousUser()

    def test_predefined_view_type(self):
        class TestView(AutoPermissionRequiredMixin, CreateView):
            model = self.model
            fields = ()

        self.assertEqual(TestView.as_view()(self.req).status_code, 200)

    def test_custom_view_type(self):
        class CustomViewMixin:
            pass

        class TestView(AutoPermissionRequiredMixin, CustomViewMixin, CreateView):
            model = self.model
            fields = ()
            permission_type_map = [
                (CustomViewMixin, "unknown_perm")
            ] + AutoPermissionRequiredMixin.permission_type_map
            raise_exception = True

        with self.assertRaises(PermissionDenied):
            TestView.as_view()(self.req)

    def test_unknown_view_type(self):
        class TestView(AutoPermissionRequiredMixin, View):
            pass

        with self.assertRaises(ImproperlyConfigured):
            TestView.as_view()(self.req)

    def test_overwrite_perm_type(self):
        class TestView(AutoPermissionRequiredMixin, CreateView):
            model = self.model
            fields = ()
            permission_type = "unknown"
            raise_exception = True

        with self.assertRaises(PermissionDenied):
            TestView.as_view()(self.req)

    def test_disable_perm_checking(self):
        class TestView(AutoPermissionRequiredMixin, CreateView):
            model = self.model
            fields = ()
            permission_type = None

        self.assertEqual(TestView.as_view()(self.req).status_code, 200)

    def test_permission_required_passthrough(self):
        class TestView(AutoPermissionRequiredMixin, CreateView):
            model = self.model
            fields = ()
            permission_required = "testapp.unknown_perm"
            raise_exception = True

        with self.assertRaises(PermissionDenied):
            TestView.as_view()(self.req)
