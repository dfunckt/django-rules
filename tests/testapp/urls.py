from django.contrib import admin
from django.urls import re_path

from .views import (
    BookCreateView,
    BookDeleteView,
    BookUpdateErrorView,
    BookUpdateView,
    ViewThatRaises,
    ViewWithPermissionList,
    change_book,
    delete_book,
    view_that_raises,
    view_with_object,
    view_with_permission_list,
)

admin.autodiscover()

urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    # Function-based views
    re_path(r"^(?P<book_id>\d+)/change/$", change_book, name="change_book"),
    re_path(r"^(?P<book_id>\d+)/delete/$", delete_book, name="delete_book"),
    re_path(r"^(?P<book_id>\d+)/raise/$", view_that_raises, name="view_that_raises"),
    re_path(r"^(?P<book_id>\d+)/object/$", view_with_object, name="view_with_object"),
    re_path(
        r"^(?P<book_id>\d+)/list/$",
        view_with_permission_list,
        name="view_with_permission_list",
    ),
    # Class-based views
    re_path(r"^cbv/create/$", BookCreateView.as_view(), name="cbv.create_book"),
    re_path(
        r"^cbv/(?P<book_id>\d+)/change/$",
        BookUpdateView.as_view(),
        name="cbv.change_book",
    ),
    re_path(
        r"^cbv/(?P<book_id>\d+)/delete/$",
        BookDeleteView.as_view(),
        name="cbv.delete_book",
    ),
    re_path(
        r"^cbv/(?P<book_id>\d+)/raise/$",
        ViewThatRaises.as_view(),
        name="cbv.view_that_raises",
    ),
    re_path(
        r"^cbv/(?P<book_id>\d+)/list/$",
        ViewWithPermissionList.as_view(),
        name="cbv.view_with_permission_list",
    ),
    re_path(
        r"^cbv/(?P<book_id>\d+)/change-error/$",
        BookUpdateErrorView.as_view(),
        name="cbv.change_book_error",
    ),
]
