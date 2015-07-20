from __future__ import absolute_import

from django.contrib import admin
from rules.contrib.admin import ObjectPermissionsModelAdmin
from .models import Book


class BookAdmin(ObjectPermissionsModelAdmin):
    pass


admin.site.register(Book, BookAdmin)
