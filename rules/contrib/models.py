from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db.models import Model
from django.db.models.base import ModelBase
from django.shortcuts import get_object_or_404

from rules.compat.six import string_types, wraps
from .views import _redirect_to_login
from ..permissions import add_perm


class RulesModelBaseMixin:
    """
    Mixin for the metaclass of Django's Model that allows declaring object-level
    permissions in the model's Meta options.

    If set, the Meta attribute "rules_permissions" has to be a dictionary with
    permission types (like "add" or "change") as keys and predicates (like
    rules.is_staff) as values. Permissions are then registered with the rules
    framework automatically upon Model creation.

    This mixin can be used for creating custom metaclasses.
    """

    def __new__(cls, name, bases, attrs, **kwargs):
        model_meta = attrs.get("Meta")
        if hasattr(model_meta, "rules_permissions"):
            perms = model_meta.rules_permissions
            del model_meta.rules_permissions
            if not isinstance(perms, dict):
                raise ImproperlyConfigured(
                    "The rules_permissions Meta option of %s must be a dict, not %s."
                    % (name, type(perms))
                )
            perms = perms.copy()
        else:
            perms = {}

        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        new_class._meta.rules_permissions = perms
        new_class.preprocess_rules_permissions(perms)
        for perm_type, predicate in perms.items():
            add_perm(new_class.get_perm(perm_type), predicate)
        return new_class


class RulesModelBase(RulesModelBaseMixin, ModelBase):
    """
    A subclass of Django's ModelBase with the RulesModelBaseMixin mixed in.
    """


class RulesModelMixin:
    """
    A mixin for Django's Model that adds hooks for stepping into the process of
    permission registration, which are called by the metaclass implementation in
    RulesModelBaseMixin.

    Use this mixin in a custom subclass of Model in order to change its behavior.
    """

    @classmethod
    def get_perm(cls, perm_type):
        """Converts permission type ("add") to permission name ("app.add_modelname")

        :param perm_type: "add", "change", etc., or custom value
        :type  perm_type: str
        :returns str:
        """
        return "%s.%s_%s" % (cls._meta.app_label, perm_type, cls._meta.model_name)

    @classmethod
    def preprocess_rules_permissions(cls, perms):
        """May alter a permissions dict before it's processed further.

        Use this, for instance, to alter the supplied permissions or insert default
        values into the given dict.

        :param perms:
            Shallow-copied value of the rules_permissions model Meta option
        :type  perms: dict
        """

    @classmethod
    def permission_required(cls, perm, login_url=None, raise_exception=False, redirect_field_name=REDIRECT_FIELD_NAME):
        """
        View decorator that checks for the permission on a class.

        Use it like this:

            from posts.models import Post

            @Post.permission_required('change')
            def post_update(request, post_id):
                # ...

        This is an alternative to writing `@permission_required("myapp.change_post")`. If you want to check for
        permissions on a specific object, `see object_permission_required`.

        ``perm`` is either a permission name as a string, or a list of permission
        names.

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
            @wraps(view_func)
            def _wrapped_view(request, *args, **kwargs):
                # Normalize to a list of permissions
                if isinstance(perm, string_types):
                    perms = cls.get_perm(perm)
                else:
                    perms = ( cls.get_perm(p) for p in perm )

                # Get the user
                user = request.user

                # Check for permissions and return a response
                if not user.has_perm(perms):
                    # User does not have a required permission
                    if raise_exception:
                        raise PermissionDenied()
                    else:
                        return _redirect_to_login(request, view_func.__name__, login_url, redirect_field_name)
                else:
                    # User has all required permissions -- allow the view to execute
                    return view_func(request, *args, **kwargs)

            return _wrapped_view

        return decorator

    @classmethod
    def object_permission_required(cls, perm, login_url=None, raise_exception=False, redirect_field_name=REDIRECT_FIELD_NAME, **decorator_kwargs):
        """
        View decorator that checks for the permission on Model objects. It works best with views
        that use get_object_or_404. It uses the parameters passed throught the url mapping to get an
        object and test for permissions, or raises a 404 error if the object does not exist.

        Use it like this:

            from posts.models import Post

            @Post.object_permission_required('change', pk="post_id")
            def post_update(request, post_id):
                # ...
                post = get_object_or_404(pk=post_id)
                # ....

        ``perm`` is either a permission name as a string, or a list of permission
        names

        After that, the optional arguments ``login_url``, ``raise_exception`` and ``redirect_field_names``
        can be passed (see below). Any arguments after that are strings that specify the names of the arguments to pass
        to get_object_or_404. So he argument `pk="post_id"` in the example above will look up the `post_id` argument
        passed to the view function, and pass that as the `pk` argument to get_object_or_404. This means that there will
        be two calls to get_object_or_404: one in the object_permission_required decorator, to check the permission,
        and a second one inside the view function.

        Another example:

            from books.models import Book

            @Book.object_permission_required('read', title="name", author="author")
            def read_book(request, name, author):
                # ...
                book = call get_object_or_404(title=name, author=author)
                # ...

        Here, the `name` and `author` arguments will be taken from the url, and passed to get_object_or_404 as
        `title` and `author`, respectively.

        If you do not specify any keyword arguments, this will assume you have an argument `id` that will be used as
        a primary key. So the following will call get_object_or_404(pk=id):

            from todo.models import Todo

            @Todo.object_permission_required('mark_done')
            def mark_as_done(request, id):
                # ...
                get_object_or_404(pk=id)
                # ...

    Other optional arguments:

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
            @wraps(view_func)
            def _wrapped_view(request, *args, **kwargs):
                if not kwargs:
                    get_object_kwargs = {"pk": "id"}
                else:
                    try:
                        get_object_kwargs = {name: kwargs[value] for name, value in decorator_kwargs.items()}
                    except KeyError as error:
                        raise ImproperlyConfigured('Argument {0} is not available. Given arguments: [{1}]'
                .format(str(error), ', '.join(decorator_kwargs.values())))

                # Get the object to check permissions against
                obj = get_object_or_404(cls, **get_object_kwargs)

                # Get the user
                user = request.user

                # Normalize to a list of permissions
                if isinstance(perm, string_types):
                    perms = cls.get_perm(perm)
                else:
                    perms = ( cls.get_perm(p) for p in perm )

                # Check for permissions and return a response
                if not user.has_perm(perms, obj):
                    # User does not have a required permission
                    if raise_exception:
                        raise PermissionDenied()
                    else:
                        return _redirect_to_login(request, view_func.__name__, login_url, redirect_field_name)
                else:
                    # User has all required permissions -- allow the view to execute
                    return view_func(request, *args, **kwargs)

            return _wrapped_view

        return decorator



class RulesModel(RulesModelMixin, Model, metaclass=RulesModelBase):
    """
    An abstract model with RulesModelMixin mixed in, using RulesModelBase as metaclass.

    Use this as base for your models directly if you don't need to customize the
    behavior of RulesModelMixin and thus don't want to create a custom base class.
    """

    class Meta:
        abstract = True
