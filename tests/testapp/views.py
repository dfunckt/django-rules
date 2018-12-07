from __future__ import absolute_import

from django.http import HttpResponse
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from rules.contrib.views import permission_required, objectgetter
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

from .models import Book


class BookMixin(object):
    def get_object(self):
        return Book.objects.get(pk=self.kwargs['book_id'])


class BookMixinWithError(object):
    def get_object(self):
        raise AttributeError('get_object')


@permission_required('testapp.change_book', fn=objectgetter(Book, 'book_id'))
def change_book(request, book_id):
    return HttpResponse('OK')



class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, BookMixin, CreateView):
    fields = ['title']
    template_name = 'empty.html'
    permission_required = 'testapp.create_book'


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, BookMixin, UpdateView):
    fields = ['title']
    template_name = 'empty.html'
    permission_required = 'testapp.change_book'


class BookUpdateErrorView(LoginRequiredMixin, PermissionRequiredMixin, BookMixinWithError, UpdateView):
    fields = ['title']
    template_name = 'empty.html'
    permission_required = 'testapp.change_book'


@permission_required('testapp.delete_book', fn=objectgetter(Book, 'book_id'))
def delete_book(request, book_id):
    return HttpResponse('OK')


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, BookMixin, DeleteView):
    template_name = 'empty.html'
    permission_required = 'testapp.delete_book'


@permission_required('testapp.delete_book', fn=objectgetter(Book, 'book_id'), raise_exception=True)
def view_that_raises(request, book_id):
    return HttpResponse('OK')


class ViewThatRaises(LoginRequiredMixin, PermissionRequiredMixin, BookMixin, DeleteView):
    template_name = 'empty.html'
    raise_exception = True
    permission_required = 'testapp.delete_book'


@permission_required(['testapp.change_book', 'testapp.delete_book'], fn=objectgetter(Book, 'book_id'))
def view_with_permission_list(request, book_id):
    return HttpResponse('OK')


class ViewWithPermissionList(LoginRequiredMixin, PermissionRequiredMixin, BookMixin, DeleteView):
    template_name = 'empty.html'
    permission_required = ['testapp.change_book', 'testapp.delete_book']


@permission_required('testapp.delete_book', fn=objectgetter(Book, 'book_id'))
def view_with_object(request, book_id):
    return HttpResponse('OK')
