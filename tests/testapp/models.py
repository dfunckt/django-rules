from __future__ import absolute_import

from django.conf import settings
from django.db import models

import rules
from rules.contrib.models import RulesModel


class Book(models.Model):
    isbn = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TestModel(RulesModel):
    class Meta:
        rules_permissions = {
            "add": {'pred': rules.always_true, 'verbose_name': "Add"},
            "view": rules.always_true,
        }

    @classmethod
    def preprocess_rules_permissions(cls, perms):
        perms["custom"] = {'pred': rules.always_true, 'verbose_name': "Custom Perm"}
        perms["custom2"] = rules.always_true
