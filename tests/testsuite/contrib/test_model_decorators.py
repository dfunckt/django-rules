from __future__ import absolute_import

import sys
import unittest

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpRequest, Http404
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.encoding import force_str
from django.views.generic import CreateView, View

import rules
from rules.contrib.views import AutoPermissionRequiredMixin, objectgetter

from . import TestData

if sys.version_info.major >= 3:
    from testapp.models import Car

@unittest.skipIf(sys.version_info.major < 3,  "Python 3 only")
class ModelDecoratorTests(TestData, TestCase):

    def test_object_permission_required(self):
        # Adrian can wash his car
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("wash_car", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin can wash Adrian's car
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("wash_car", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Adrian can drive his car
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("drive_car", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin can *not* drive adrians car
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("drive_car", args=(1,)))
        self.assertEqual(response.status_code, 302)

        # Martin can *not* crash Adrian's book and an PermissionDenied is raised
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("crash_car", args=(1,)))
        self.assertEqual(response.status_code, 403)

        # Test views that require a list of permissions

        # Adrian has both permissions
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("car_view_with_permission_list", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin does not have delete permission
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("car_view_with_permission_list", args=(1,)))
        self.assertEqual(response.status_code, 302)

    def test_object_permission_required_with_default(self):
        # Adrian can wash his car
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("wash_car_default", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin can wash Adrian's car
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("wash_car_default", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Adrian can drive his car
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("drive_car_default", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin can *not* drive adrians car
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("drive_car_default", args=(1,)))
        self.assertEqual(response.status_code, 302)

        # Martin can *not* crash Adrian's book and an PermissionDenied is raised
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("crash_car_default", args=(1,)))
        self.assertEqual(response.status_code, 403)


    def test_permission_required(self):
        # Test the decorators for class-level permissions
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("wash_class"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin can wash Adrian's car
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("wash_class"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin can *not* crash and an PermissionDenied is raised
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("crash_class"))
        self.assertEqual(response.status_code, 403)

        # Test views that require a list of permissions

        # Adrian has both permissions
        self.assertTrue(self.client.login(username="adrian", password="secr3t"))
        response = self.client.get(reverse("car_view_with_permission_list_for_class"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(force_str(response.content), "OK")

        # Martin does not have delete permission
        self.assertTrue(self.client.login(username="martin", password="secr3t"))
        response = self.client.get(reverse("car_view_with_permission_list_for_class"))
        self.assertEqual(response.status_code, 302)