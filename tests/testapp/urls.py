import sys

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

if sys.version_info.major >= 3:
    from .views import (drive_car, wash_car, crash_car, car_view_with_permission_list,
                        wash, crash, car_view_with_permission_list_for_class,
                        wash_car_default, crash_car_default, drive_car_default)
    urlpatterns += [
        url(r'^(?P<car_id>\d+)/drive/$', drive_car, name='drive_car'),
        url(r'^(?P<car_id>\d+)/wash/$', wash_car, name='wash_car'),
        url(r'^(?P<car_id>\d+)/crash/$', crash_car, name='crash_car'),
        url(r'^(?P<car_id>\d+)/permlist/$', car_view_with_permission_list, name='car_view_with_permission_list'),
        url(r'^(?P<id>\d+)/drive_default/$', drive_car_default, name='drive_car_default'),
        url(r'^(?P<id>\d+)/wash_default/$', wash_car_default, name='wash_car_default'),
        url(r'^(?P<id>\d+)/crash_default/$', crash_car_default, name='crash_car_default'),
        url(r'^wash$', wash, name='wash_class'),
        url(r'^crash$', crash, name='crash_class'),
        url(r'^permlist$', car_view_with_permission_list_for_class, name='car_view_with_permission_list_for_class'),
    ]