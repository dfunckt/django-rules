from __future__ import absolute_import

from django.http import HttpResponse

from rules.contrib.views import permission_required, objectgetter

from .models import Book


@permission_required('testapp.change_book', fn=objectgetter(Book, 'book_id'))
def change_book(request, book_id):
    return HttpResponse('OK')


@permission_required('testapp.delete_book', fn=objectgetter(Book, 'book_id'))
def delete_book(request, book_id):
    return HttpResponse('OK')


@permission_required('testapp.delete_book', fn=objectgetter(Book, 'book_id'), raise_exception=True)
def view_that_raises(request, book_id):
    return HttpResponse('OK')


@permission_required(['testapp.change_book', 'testapp.delete_book'], fn=objectgetter(Book, 'book_id'))
def view_with_permission_list(request, book_id):
    return HttpResponse('OK')


@permission_required('testapp.delete_book', fn=Book.objects.get(pk=1))
def view_with_object(request, book_id):
    return HttpResponse('OK')
