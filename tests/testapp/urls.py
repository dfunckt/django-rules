from django.conf.urls import include, url
from django.contrib import admin

from .views import BookUpdateView, BookDeleteView, ViewThatRaises, ViewWithPermissionList

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    # Function-based views
    url(r'^(?P<book_id>\d+)/change/$', 'testapp.views.change_book', name='change_book'),
    url(r'^(?P<book_id>\d+)/delete/$', 'testapp.views.delete_book', name='delete_book'),
    url(r'^(?P<book_id>\d+)/raise/$', 'testapp.views.view_that_raises', name='view_that_raises'),
    url(r'^(?P<book_id>\d+)/object/$', 'testapp.views.view_with_object', name='view_with_object'),
    url(r'^(?P<book_id>\d+)/list/$', 'testapp.views.view_with_permission_list', name='view_with_permission_list'),

    # Class-based views
    url(r'^cbv/(?P<book_id>\d+)/change/$', BookUpdateView.as_view(), name='cbv.change_book'),
    url(r'^cbv/(?P<book_id>\d+)/delete/$', BookDeleteView.as_view(), name='cbv.delete_book'),
    url(r'^cbv/(?P<book_id>\d+)/raise/$', ViewThatRaises.as_view(), name='cbv.view_that_raises'),
    url(r'^cbv/(?P<book_id>\d+)/list/$', ViewWithPermissionList.as_view(), name='cbv.view_with_permission_list'),
]
