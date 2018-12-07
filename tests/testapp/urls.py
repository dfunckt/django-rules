from django.conf.urls import url
from django.contrib import admin

from .views import (change_book, delete_book,
                    view_that_raises, view_with_object, view_with_permission_list,
                    BookUpdateView, BookDeleteView, ViewThatRaises, ViewWithPermissionList,
                    BookUpdateErrorView, BookCreateView)

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Function-based views
    url(r'^(?P<book_id>\d+)/change/$', change_book, name='change_book'),
    url(r'^(?P<book_id>\d+)/delete/$', delete_book, name='delete_book'),
    url(r'^(?P<book_id>\d+)/raise/$', view_that_raises, name='view_that_raises'),
    url(r'^(?P<book_id>\d+)/object/$', view_with_object, name='view_with_object'),
    url(r'^(?P<book_id>\d+)/list/$', view_with_permission_list, name='view_with_permission_list'),

    # Class-based views
    url(r'^cbv/create/$', BookCreateView.as_view(), name='cbv.create_book'),
    url(r'^cbv/(?P<book_id>\d+)/change/$', BookUpdateView.as_view(), name='cbv.change_book'),
    url(r'^cbv/(?P<book_id>\d+)/delete/$', BookDeleteView.as_view(), name='cbv.delete_book'),
    url(r'^cbv/(?P<book_id>\d+)/raise/$', ViewThatRaises.as_view(), name='cbv.view_that_raises'),
    url(r'^cbv/(?P<book_id>\d+)/list/$', ViewWithPermissionList.as_view(), name='cbv.view_with_permission_list'),

    url(r'^cbv/(?P<book_id>\d+)/change-error/$', BookUpdateErrorView.as_view(), name='cbv.change_book_error'),
]
