from functools import wraps

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import mixins
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ImproperlyConfigured, FieldError
from django.shortcuts import get_object_or_404
from django.utils import six
from django.utils.decorators import available_attrs
from django.utils.encoding import force_text


# These are made available for convenience, as well as for use in Django
# versions before 1.9. For usage help see Django's docs for 1.9 or later.
from django.views.generic.edit import BaseCreateView

LoginRequiredMixin = mixins.LoginRequiredMixin
UserPassesTestMixin = mixins.UserPassesTestMixin


class PermissionRequiredMixin(mixins.PermissionRequiredMixin):
    """
    CBV mixin to provide object-level permission checking to views. Best used
    with views that inherit from ``SingleObjectMixin`` (``DetailView``,
    ``UpdateView``, etc.), though not required.

    The single requirement is for a ``get_object`` method to be available
    in the view. If there's no ``get_object`` method, permission checking
    is model-level, that is exactly like Django's ``PermissionRequiredMixin``.
    """
    def get_permission_object(self):
        """
        Override this method to provide the object to check for permission
        against. By default uses ``self.get_object()`` as provided by
        ``SingleObjectMixin``. Returns None if there's no ``get_object``
        method.
        """
        if not isinstance(self, BaseCreateView):
            # We do NOT want to call get_object in a BaseCreateView, see issue #85
            if hasattr(self, 'get_object') and callable(self.get_object):
                # Requires SingleObjectMixin or equivalent ``get_object`` method
                return self.get_object()
        return None

    def has_permission(self):
        obj = self.get_permission_object()
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms, obj)


def objectgetter(model, attr_name='pk', field_name='pk'):
    """
    Helper that returns a function suitable for use as the ``fn`` argument
    to the ``permission_required`` decorator. Internally uses
    ``get_object_or_404``, so keep in mind that this may raise ``Http404``.

    ``model`` can be a model class, manager or queryset.

    ``attr_name`` is the name of the view attribute.

    ``field_name`` is the model's field name by which the lookup is made, eg.
    "id", "slug", etc.
    """
    def _getter(request, *view_args, **view_kwargs):
        if attr_name not in view_kwargs:
            raise ImproperlyConfigured(
                'Argument {0} is not available. Given arguments: [{1}]'
                .format(attr_name, ', '.join(view_kwargs.keys())))
        try:
            return get_object_or_404(model, **{field_name: view_kwargs[attr_name]})
        except FieldError:
            raise ImproperlyConfigured(
                'Model {0} has no field named {1}'
                .format(model, field_name))
    return _getter


def permission_required(perm, fn=None, login_url=None, raise_exception=False, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    View decorator that checks for the given permissions before allowing the
    view to execute. Use it like this::

        from django.shortcuts import get_object_or_404
        from rules.contrib.views import permission_required
        from posts.models import Post

        def get_post_by_pk(request, post_id):
            return get_object_or_404(Post, pk=post_id)

        @permission_required('posts.change_post', fn=get_post_by_pk)
        def post_update(request, post_id):
            # ...

    ``perm`` is either a permission name as a string, or a list of permission
    names.

    ``fn`` is an optional callback that receives the same arguments as those
    passed to the decorated view and must return the object to check
    permissions against. If omitted, the decorator behaves just like Django's
    ``permission_required`` decorator, i.e. checks for model-level permissions.

    ``raise_exception`` is a boolean specifying whether to raise a
    ``django.core.exceptions.PermissionDenied`` exception if the check fails.
    You will most likely want to set this argument to ``True`` if you have
    specified a custom 403 response handler in your urlconf. If ``False``,
    the user will be redirected to the URL specified by ``login_url``.

    ``login_url`` is an optional custom URL to redirect the user to if
    permissions check fails. If omitted or empty, ``settings.LOGIN_URL`` is
    used.
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            # Normalize to a list of permissions
            if isinstance(perm, six.string_types):
                perms = (perm,)
            else:
                perms = perm

            # Get the object to check permissions against
            if callable(fn):
                obj = fn(request, *args, **kwargs)
            else:  # pragma: no cover
                obj = fn

            # Get the user
            user = request.user

            # Check for permissions and return a response
            if not user.has_perms(perms, obj):
                # User does not have a required permission
                if raise_exception:
                    raise PermissionDenied()
                else:
                    return _redirect_to_login(request, view_func.__name__,
                                              login_url, redirect_field_name)
            else:
                # User has all required permissions -- allow the view to execute
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def _redirect_to_login(request, view_name, login_url, redirect_field_name):
    redirect_url = login_url or settings.LOGIN_URL
    if not redirect_url:  # pragma: no cover
        raise ImproperlyConfigured(
            'permission_required({0}): You must either provide '
            'the "login_url" argument to the "permission_required" '
            'decorator or configure settings.LOGIN_URL'.format(view_name)
        )
    redirect_url = force_text(redirect_url)
    return redirect_to_login(request.get_full_path(), redirect_url, redirect_field_name)
