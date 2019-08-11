from __future__ import absolute_import

import sys

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import rules


@python_2_unicode_compatible
class Book(models.Model):
    isbn = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


if sys.version_info.major >= 3:
    from rules.contrib.models import RulesModel

    class TestModel(RulesModel):
        class Meta:
            rules_permissions = {"add": rules.always_true, "view": rules.always_true}

        @classmethod
        def preprocess_rules_permissions(cls, perms):
            perms["custom"] = rules.always_true
