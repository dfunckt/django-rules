from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^(?P<book_id>\d+)/change/$', 'testapp.views.change_book', name='change_book'),
    url(r'^(?P<book_id>\d+)/delete/$', 'testapp.views.delete_book', name='delete_book'),
    url(r'^(?P<book_id>\d+)/raise/$', 'testapp.views.view_that_raises', name='view_that_raises'),
    url(r'^(?P<book_id>\d+)/object/$', 'testapp.views.view_with_object', name='view_with_object'),
    url(r'^(?P<book_id>\d+)/list/$', 'testapp.views.view_with_permission_list', name='view_with_permission_list'),
]
