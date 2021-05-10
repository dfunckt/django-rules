from __future__ import absolute_import

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

import rules


class RulesModelTests(TestCase):
    def test_preprocess(self):
        self.assertTrue(rules.perm_exists("testapp.add_testmodel"))
        self.assertTrue(rules.perm_exists("testapp.custom_testmodel"))

    def test_invalid_config(self):
        from rules.contrib.models import RulesModel

        with self.assertRaises(ImproperlyConfigured):

            class InvalidTestModel(RulesModel):
                class Meta:
                    app_label = "testapp"
                    rules_permissions = "invalid"
