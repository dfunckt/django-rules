rules
^^^^^

``rules`` is a tiny but powerful app providing object-level permissions to
Django, without requiring a database. At its core, it is a generic framework
for building rule-based systems, similar to `decision trees`_. It can also be
used as a standalone library in other contexts and frameworks.

.. image:: https://img.shields.io/github/workflow/status/dfunckt/django-rules/CI/master
    :target: https://github.com/dfunckt/django-rules/actions
.. image:: https://coveralls.io/repos/dfunckt/django-rules/badge.svg
    :target: https://coveralls.io/r/dfunckt/django-rules
.. image:: https://img.shields.io/pypi/v/rules.svg
    :target: https://pypi.org/project/rules/
.. image:: https://img.shields.io/pypi/pyversions/rules.svg
    :target: https://pypi.org/project/rules/
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://github.com/pre-commit/pre-commit

.. _decision trees: http://wikipedia.org/wiki/Decision_tree


Features
========

``rules`` has got you covered. ``rules`` is:

-   **Documented**, **tested**, **reliable** and **easy to use**.
-   **Versatile**. Decorate callables to build complex graphs of predicates.
    Predicates can be any type of callable -- simple functions, lambdas,
    methods, callable class objects, partial functions, decorated functions,
    anything really.
-   **A good Django citizen**. Seamless integration with Django views,
    templates and the Admin for testing for object-level permissions.
-   **Efficient** and **smart**. No need to mess around with a database to figure
    out whether John really wrote that book.
-   **Simple**. Dive in the code. You'll need 10 minutes to figure out how it
    works.
-   **Powerful**. ``rules`` comes complete with advanced features, such as
    invocation context and storage for arbitrary data, skipping evaluation of
    predicates under specific conditions, logging of evaluated predicates and more!


Table of Contents
=================

- `Requirements`_
- `Upgrading from 2.x`_
- `Upgrading from 1.x`_
- `How to install`_

  - `Configuring Django`_

- `Using Rules`_

  - `Creating predicates`_
  - `Setting up rules`_
  - `Combining predicates`_

- `Using Rules with Django`_

  - `Permissions`_
  - `Permissions in models`_
  - `Permissions in views`_
  - `Permissions and rules in templates`_
  - `Permissions in the Admin`_
  - `Permissions in Django Rest Framework`_

- `Advanced features`_

  - `Custom rule sets`_
  - `Invocation context`_
  - `Binding "self"`_
  - `Skipping predicates`_
  - `Logging predicate evaluation`_

- `Best practices`_
- `API Reference`_
- `Licence`_


Requirements
============

``rules`` requires Python 3.7 or newer. The last version to support Python 2.7
is ``rules`` 2.2. It can optionally integrate with Django, in which case
requires Django 2.2 or newer.

*Note*: At any given moment in time, ``rules`` will maintain support for all
currently supported Django versions, while dropping support for those versions
that reached end-of-life in minor releases. See the `Supported Versions`_
section on Django Project website for the current state and timeline.

.. _Supported Versions: https://www.djangoproject.com/download/#supported-versions


Upgrading from 2.x
==================

The are no significant changes between ``rules`` 2.x and 3.x except dropping
support for Python 2, so before upgrading to 3.x you just need to make sure
you're running a supported Python 3 version.


Upgrading from 1.x
==================

*   Support for Python 2.6 and 3.3, and Django versions before 1.11 has been
    dropped.

*   The ``SkipPredicate`` exception and ``skip()`` method of ``Predicate``,
    that were used to signify that a predicate should be skipped, have been
    removed. You may return ``None`` from your predicate to achieve this.

*   The APIs to replace a rule's predicate have been renamed and their
    behaviour changed. ``replace_rule`` and ``replace_perm`` functions and
    ``replace_rule`` method of ``RuleSet`` have been renamed to ``set_rule``,
    ``set_perm`` and ``RuleSet.set_perm`` respectively. The old behaviour was
    to raise a ``KeyError`` if a rule by the given name did not exist. Since
    version 2.0 this has changed and you can safely use ``set_*`` to set a
    rule's predicate without having to ensure the rule exists first.


How to install
==============

Using pip:

.. code:: bash

    $ pip install rules

Manually:

.. code:: bash

    $ git clone https://github.com/dfunckt/django-rules.git
    $ cd django-rules
    $ python setup.py install

Run tests with:

.. code:: bash

    $ ./runtests.sh

You may also want to read `Best practices`_ for general advice on how to
use ``rules``.


Configuring Django
------------------

Add ``rules`` to ``INSTALLED_APPS``:

.. code:: python

    INSTALLED_APPS = (
        # ...
        'rules',
    )

Add the authentication backend:

.. code:: python

    AUTHENTICATION_BACKENDS = (
        'rules.permissions.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
    )


Using Rules
===========

``rules`` is based on the idea that you maintain a dict-like object that maps
string keys used as identifiers of some kind, to callables, called
*predicates*. This dict-like object is actually an instance of ``RuleSet`` and
the predicates are instances of ``Predicate``.


Creating predicates
-------------------

Let's ignore rule sets for a moment and go ahead and define a predicate. The
easiest way is with the ``@predicate`` decorator:

.. code:: python

    >>> @rules.predicate
    >>> def is_book_author(user, book):
    ...     return book.author == user
    ...
    >>> is_book_author
    <Predicate:is_book_author object at 0x10eeaa490>

This predicate will return ``True`` if the book's author is the given user,
``False`` otherwise.

Predicates can be created from any callable that accepts anything from zero to
two positional arguments:

*   ``fn(obj, target)``
*   ``fn(obj)``
*   ``fn()``

This is their generic form. If seen from the perspective of authorization in
Django, the equivalent signatures are:

*   ``fn(user, obj)``
*   ``fn(user)``
*   ``fn()``

Predicates can do pretty much anything with the given arguments, but must
always return ``True`` if the condition they check is true, ``False``
otherwise. ``rules`` comes with several predefined predicates that you may
read about later on in `API Reference`_, that are mostly useful when dealing
with `authorization in Django`_.


Setting up rules
----------------

Let's pretend that we want to let authors edit or delete their books, but not
books written by other authors. So, essentially, what determines whether an
author *can edit* or *can delete* a given book is *whether they are its
author*.

In ``rules``, such requirements are modelled as *rules*. A *rule* is a map of
a unique identifier (eg. "can edit") to a predicate. Rules are grouped
together into a *rule set*. ``rules`` has two predefined rule sets:

*   A default rule set storing shared rules.
*   Another rule set storing rules that serve as permissions in a Django
    context.

So, let's define our first couple of rules, adding them to the shared rule
set. We can use the ``is_book_author`` predicate we defined earlier:

.. code:: python

    >>> rules.add_rule('can_edit_book', is_book_author)
    >>> rules.add_rule('can_delete_book', is_book_author)

Assuming we've got some data, we can now test our rules:

.. code:: python

    >>> from django.contrib.auth.models import User
    >>> from books.models import Book
    >>> guidetodjango = Book.objects.get(isbn='978-1-4302-1936-1')
    >>> guidetodjango.author
    <User: adrian>
    >>> adrian = User.objects.get(username='adrian')
    >>> rules.test_rule('can_edit_book', adrian, guidetodjango)
    True
    >>> rules.test_rule('can_delete_book', adrian, guidetodjango)
    True

Nice... but not awesome.


Combining predicates
--------------------

Predicates by themselves are not so useful -- not more useful than any other
function would be. Predicates, however, can be combined using binary operators
to create more complex ones. Predicates support the following operators:

*   ``P1 & P2``: Returns a new predicate that returns ``True`` if *both*
    predicates return ``True``, otherwise ``False``. If P1 returns ``False``,
    P2 will not be evaluated.
*   ``P1 | P2``: Returns a new predicate that returns ``True`` if *any* of the
    predicates returns ``True``, otherwise ``False``. If P1 returns ``True``,
    P2 will not be evaluated.
*   ``P1 ^ P2``: Returns a new predicate that returns ``True`` if one of the
    predicates returns ``True`` and the other returns ``False``, otherwise
    ``False``.
*   ``~P``: Returns a new predicate that returns the negated result of the
    original predicate.

Suppose the requirement for allowing a user to edit a given book was for them
to be either the book's author, or a member of the "editors" group. Allowing
users to delete a book should still be determined by whether the user is the
book's author.

With ``rules`` that's easy to implement. We'd have to define another
predicate, that would return ``True`` if the given user is a member of the
"editors" group, ``False`` otherwise. The built-in ``is_group_member`` factory
will come in handy:

.. code:: python

    >>> is_editor = rules.is_group_member('editors')
    >>> is_editor
    <Predicate:is_group_member:editors object at 0x10eee1350>

We could combine it with the ``is_book_author`` predicate to create a new one
that checks for either condition:

.. code:: python

    >>> is_book_author_or_editor = is_book_author | is_editor
    >>> is_book_author_or_editor
    <Predicate:(is_book_author | is_group_member:editors) object at 0x10eee1390>

We can now update our ``can_edit_book`` rule:

.. code:: python

    >>> rules.set_rule('can_edit_book', is_book_author_or_editor)
    >>> rules.test_rule('can_edit_book', adrian, guidetodjango)
    True
    >>> rules.test_rule('can_delete_book', adrian, guidetodjango)
    True

Let's see what happens with another user:

.. code:: python

    >>> martin = User.objects.get(username='martin')
    >>> list(martin.groups.values_list('name', flat=True))
    ['editors']
    >>> rules.test_rule('can_edit_book', martin, guidetodjango)
    True
    >>> rules.test_rule('can_delete_book', martin, guidetodjango)
    False

Awesome.

So far, we've only used the underlying, generic framework for defining and
testing rules. This layer is not at all specific to Django; it may be used in
any context. There's actually no import of anything Django-related in the
whole app (except in the ``rules.templatetags`` module). ``rules`` however can
integrate tightly with Django to provide authorization.


.. _authorization in Django:

Using Rules with Django
=======================

``rules`` is able to provide object-level permissions in Django. It comes
with an authorization backend and a couple template tags for use in your
templates.


Permissions
-----------

In ``rules``, permissions are a specialised type of rules. You still define
rules by creating and combining predicates. These rules however, must be added
to a permissions-specific rule set that comes with ``rules`` so that they can
be picked up by the ``rules`` authorization backend.


Creating permissions
++++++++++++++++++++

The convention for naming permissions in Django is ``app_label.action_object``,
and we like to adhere to that. Let's add rules for the ``books.change_book``
and ``books.delete_book`` permissions:

.. code:: python

    >>> rules.add_perm('books.change_book', is_book_author | is_editor)
    >>> rules.add_perm('books.delete_book', is_book_author)

See the difference in the API? ``add_perm`` adds to a permissions-specific
rule set, whereas ``add_rule`` adds to a default shared rule set. It's
important to know however, that these two rule sets are separate, meaning that
adding a rule in one does not make it available to the other.


Checking for permission
+++++++++++++++++++++++

Let's go ahead and check whether ``adrian`` has change permission to the
``guidetodjango`` book:

.. code:: python

    >>> adrian.has_perm('books.change_book', guidetodjango)
    False

When you call the ``User.has_perm`` method, Django asks each backend in
``settings.AUTHENTICATION_BACKENDS`` whether a user has the given permission
for the object. When queried for object permissions, Django's default
authentication backend always returns ``False``. ``rules`` comes with an
authorization backend, that is able to provide object-level permissions by
looking into the permissions-specific rule set.

Let's add the ``rules`` authorization backend in settings:

.. code:: python

    AUTHENTICATION_BACKENDS = (
        'rules.permissions.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

Now, checking again gives ``adrian`` the required permissions:

.. code:: python

    >>> adrian.has_perm('books.change_book', guidetodjango)
    True
    >>> adrian.has_perm('books.delete_book', guidetodjango)
    True
    >>> martin.has_perm('books.change_book', guidetodjango)
    True
    >>> martin.has_perm('books.delete_book', guidetodjango)
    False

**NOTE:** Calling `has_perm` on a superuser will ALWAYS return `True`.

Permissions in models
---------------------

**NOTE:** The features described in this section work on Python 3+ only.

It is common to have a set of permissions for a model, like what Django offers with
its default model permissions (such as *add*, *change* etc.). When using ``rules``
as the permission checking backend, you can declare object-level permissions for
any model in a similar way, using a new ``Meta`` option.

First, you need to switch your model's base and metaclass to the slightly extended
versions provided in ``rules.contrib.models``. There are several classes and mixins
you can use, depending on whether you're already using a custom base and/or metaclass
for your models or not. The extensions are very slim and don't affect the models'
behavior in any way other than making it register permissions.

* If you're using the stock ``django.db.models.Model`` as base for your models,
  simply switch over to ``RulesModel`` and you're good to go.

* If you already have a custom base class adding common functionality to your models,
  add ``RulesModelMixin`` to the classes it inherits from and set ``RulesModelBase``
  as its metaclass, like so::

      from django.db.models import Model
      from rules.contrib.models import RulesModelBase, RulesModelMixin

      class MyModel(RulesModelMixin, Model, metaclass=RulesModelBase):
          ...

* If you're using a custom metaclass for your models, you'll already know how to
  make it inherit from ``RulesModelBaseMixin`` yourself.

Then, create your models like so, assuming you're using ``RulesModel`` as base
directly::

    import rules
    from rules.contrib.models import RulesModel

    class Book(RulesModel):
        class Meta:
            rules_permissions = {
                "add": rules.is_staff,
                "read": rules.is_authenticated,
            }

This would be equivalent to the following calls::

    rules.add_perm("app_label.add_book", rules.is_staff)
    rules.add_perm("app_label.read_book", rules.is_authenticated)

There are methods in ``RulesModelMixin`` that you can overwrite in order to customize
how a model's permissions are registered. See the documented source code for details
if you need this.

Of special interest is the ``get_perm`` classmethod of ``RulesModelMixin``, which can
be used to convert a permission type to the corresponding full permission name. If
you need to query for some type of permission on a given model programmatically,
this is handy::

    if user.has_perm(Book.get_perm("read")):
        ...


Permissions in views
--------------------

``rules`` comes with a set of view decorators to help you enforce
authorization in your views.

Using the function-based view decorator
+++++++++++++++++++++++++++++++++++++++

For function-based views you can use the ``permission_required`` decorator:

.. code:: python

    from django.shortcuts import get_object_or_404
    from rules.contrib.views import permission_required
    from posts.models import Post

    def get_post_by_pk(request, post_id):
        return get_object_or_404(Post, pk=post_id)

    @permission_required('posts.change_post', fn=get_post_by_pk)
    def post_update(request, post_id):
        # ...

Usage is straight-forward, but there's one thing in the example above that
stands out and this is the ``get_post_by_pk`` function. This function, given
the current request and all arguments passed to the view, is responsible for
fetching and returning the object to check permissions against -- i.e. the
``Post`` instance with PK equal to the given ``post_id`` in the example.
This specific use-case is quite common so, to save you some typing, ``rules``
comes with a generic helper function that you can use to do this declaratively.
The example below is equivalent to the one above:

.. code:: python

    from rules.contrib.views import permission_required, objectgetter
    from posts.models import Post

    @permission_required('posts.change_post', fn=objectgetter(Post, 'post_id'))
    def post_update(request, post_id):
        # ...

For more information on the decorator and helper function, refer to the
``rules.contrib.views`` module.

Using the class-based view mixin
++++++++++++++++++++++++++++++++

Django includes a set of access mixins that you can use in your class-based
views to enforce authorization. ``rules`` extends this framework to provide
object-level permissions via a mixin, ``PermissionRequiredMixin``.

The following example will automatically test for permission against the
instance returned by the view's ``get_object`` method:

.. code:: python

    from django.views.generic.edit import UpdateView
    from rules.contrib.views import PermissionRequiredMixin
    from posts.models import Post

    class PostUpdate(PermissionRequiredMixin, UpdateView):
        model = Post
        permission_required = 'posts.change_post'

You can customise the object either by overriding ``get_object`` or
``get_permission_object``.

For more information refer to the `Django documentation`_ and the
``rules.contrib.views`` module.

.. _Django documentation: https://docs.djangoproject.com/en/1.9/topics/auth/default/#limiting-access-to-logged-in-users

Checking permission automatically based on view type
++++++++++++++++++++++++++++++++++++++++++++++++++++

If you use the mechanisms provided by ``rules.contrib.models`` to register permissions
for your models as described in `Permissions in models`_, there's another convenient
mixin for class-based views available for you.

``rules.contrib.views.AutoPermissionRequiredMixin`` can recognize the type of view
it's used with and check for the corresponding permission automatically.

This example view would, without any further configuration, automatically check for
the ``"posts.change_post"`` permission, given that the app label is ``"posts"``::

    from django.views.generic import UpdateView
    from rules.contrib.views import AutoPermissionRequiredMixin
    from posts.models import Post

    class UpdatePostView(AutoPermissionRequiredMixin, UpdateView):
        model = Post

By default, the generic CRUD views from ``django.views.generic`` are mapped to the
native Django permission types (*add*, *change*, *delete* and *view*). However,
the pre-defined mappings can be extended, changed or replaced altogether when
subclassing ``AutoPermissionRequiredMixin``. See the fully documented source code
for details on how to do that properly.


Permissions and rules in templates
----------------------------------

``rules`` comes with two template tags to allow you to test for rules and
permissions in templates.

Add ``rules`` to your ``INSTALLED_APPS``:

.. code:: python

    INSTALLED_APPS = (
        # ...
        'rules',
    )

Then, in your template::

    {% load rules %}

    {% has_perm 'books.change_book' author book as can_edit_book %}
    {% if can_edit_book %}
        ...
    {% endif %}

    {% test_rule 'has_super_feature' user as has_super_feature %}
    {% if has_super_feature %}
        ...
    {% endif %}


Permissions in the Admin
------------------------

If you've setup ``rules`` to be used with permissions in Django, you're almost
set to also use ``rules`` to authorize any add/change/delete actions in the
Admin. The Admin asks for *four* different permissions, depending on action:

- ``<app_label>.add_<modelname>``
- ``<app_label>.view_<modelname>``
- ``<app_label>.change_<modelname>``
- ``<app_label>.delete_<modelname>``
- ``<app_label>``

*Note:* view permission is new in Django v2.1 and should not be added in versions before that.

The first four are obvious. The fifth is the required permission for an app
to be displayed in the Admin's "dashboard". Overriding it does not restrict access to the add,
change or delete views. Here's some rules for our imaginary ``books`` app as an example:

.. code:: python

    >>> rules.add_perm('books', rules.always_allow)
    >>> rules.add_perm('books.add_book', is_staff)
    >>> rules.add_perm('books.view_book', is_staff | has_secret_access_code)
    >>> rules.add_perm('books.change_book', is_staff)
    >>> rules.add_perm('books.delete_book', is_staff)

Django Admin does not support object-permissions, in the sense that it will
never ask for permission to perform an action *on an object*, only whether a
user is allowed to act on (*any*) instances of a model.

If you'd like to tell Django whether a user has permissions on a specific
object, you'd have to override the following methods of a model's
``ModelAdmin``:

- ``has_view_permission(user, obj=None)``
- ``has_change_permission(user, obj=None)``
- ``has_delete_permission(user, obj=None)``

``rules`` comes with a custom ``ModelAdmin`` subclass,
``rules.contrib.admin.ObjectPermissionsModelAdmin``, that overrides these
methods to pass on the edited model instance to the authorization backends,
thus enabling permissions per object in the Admin:

.. code:: python

    # books/admin.py
    from django.contrib import admin
    from rules.contrib.admin import ObjectPermissionsModelAdmin
    from .models import Book

    class BookAdmin(ObjectPermissionsModelAdmin):
        pass

    admin.site.register(Book, BookAdmin)

Now this allows you to specify permissions like this:

.. code:: python

    >>> rules.add_perm('books', rules.always_allow)
    >>> rules.add_perm('books.add_book', has_author_profile)
    >>> rules.add_perm('books.change_book', is_book_author_or_editor)
    >>> rules.add_perm('books.delete_book', is_book_author)

To preserve backwards compatibility, Django will ask for either *view* or
*change* permission. For maximum flexibility, ``rules`` behaves subtly
different: ``rules`` will ask for the change permission if and only if no rule
exists for the view permission.


Permissions in Django Rest Framework
------------------------------------

Similar to ``rules.contrib.views.AutoPermissionRequiredMixin``, there is a
``rules.contrib.rest_framework.AutoPermissionViewSetMixin`` for viewsets in Django
Rest Framework. The difference is that it doesn't derive permission from the type
of view but from the API action (*create*, *retrieve* etc.) that's tried to be
performed. Of course, it also requires you to declare your models as described in
`Permissions in models`_.

Here is a possible ``ModelViewSet`` for the ``Post`` model with fully automated CRUD
permission checking::

    from rest_framework.serializers import ModelSerializer
    from rest_framework.viewsets import ModelViewSet
    from rules.contrib.rest_framework import AutoPermissionViewSetMixin
    from posts.models import Post

    class PostSerializer(ModelSerializer):
        class Meta:
            model = Post
            fields = "__all__"

    class PostViewSet(AutoPermissionViewSetMixin, ModelViewSet):
        queryset = Post.objects.all()
        serializer_class = PostSerializer

By default, the CRUD actions of ``ModelViewSet`` are mapped to the native
Django permission types (*add*, *change*, *delete* and *view*). The ``list``
action has no permission checking enabled. However, the pre-defined mappings
can be extended, changed or replaced altogether when using (or subclassing)
``AutoPermissionViewSetMixin``. Custom API actions defined via the ``@action``
decorator may then be mapped as well. See the fully documented source code for
details on how to properly customize the default behavior.


Advanced features
=================

Custom rule sets
----------------

You may create as many rule sets as you need:

.. code:: python

    >>> features = rules.RuleSet()

And manipulate them by adding, removing, querying and testing rules:

.. code:: python

    >>> features.rule_exists('has_super_feature')
    False
    >>> is_special_user = rules.is_group_member('special')
    >>> features.add_rule('has_super_feature', is_special_user)
    >>> 'has_super_feature' in features
    True
    >>> features['has_super_feature']
    <Predicate:is_group_member:special object at 0x10eeaa500>
    >>> features.test_rule('has_super_feature', adrian)
    True
    >>> features.remove_rule('has_super_feature')

Note however that custom rule sets are *not available* in Django templates --
you need to provide integration yourself.


Invocation context
------------------

A new context is created as a result of invoking ``Predicate.test()`` and is
only valid for the duration of the invocation. A context is a simple ``dict``
that you can use to store arbitrary data, (eg. caching computed values,
setting flags, etc.), that can be used by predicates later on in the chain.
Inside a predicate function it can be used like so:

.. code:: python

    >>> @predicate
    ... def mypred(a, b):
    ...     value = compute_expensive_value(a)
    ...     mypred.context['value'] = value
    ...     return True

Other predicates can later use stored values:

.. code:: python

    >>> @predicate
    ... def myotherpred(a, b):
    ...     value = myotherpred.context.get('value')
    ...     if value is not None:
    ...         return do_something_with_value(value)
    ...     else:
    ...         return do_something_without_value()

``Predicate.context`` provides a single ``args`` attribute that contains the
arguments as given to ``test()`` at the beginning of the invocation.


Binding "self"
--------------

In a predicate's function body, you can refer to the predicate instance itself
by its name, eg. ``is_book_author``. Passing ``bind=True`` as a keyword
argument to the ``predicate`` decorator will let you refer to the predicate
with ``self``, which is more convenient. Binding ``self`` is just syntactic
sugar. As a matter of fact, the following two are equivalent:

.. code:: python

    >>> @predicate
    ... def is_book_author(user, book):
    ...     if is_book_author.context.args:
    ...         return user == book.author
    ...     return False

    >>> @predicate(bind=True)
    ... def is_book_author(self, user, book):
    ...     if self.context.args:
    ...         return user == book.author
    ...     return False


Skipping predicates
-------------------

You may skip evaluation by returning ``None`` from your predicate:

.. code:: python

    >>> @predicate(bind=True)
    ... def is_book_author(self, user, book):
    ...     if len(self.context.args) > 1:
    ...         return user == book.author
    ...     else:
    ...         return None

Returning ``None`` signifies that the predicate need not be evaluated, thus
leaving the predicate result up to that point unchanged.


Logging predicate evaluation
----------------------------

``rules`` can optionally be configured to log debug information as rules are
evaluated to help with debugging your predicates. Messages are sent at the
DEBUG level to the ``'rules'`` logger. The following `dictConfig`_ configures
a console logger (place this in your project's `settings.py` if you're using
`rules` with Django):

.. code:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'rules': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }

When this logger is active each individual predicate will have a log message
printed when it is evaluated.

.. _dictConfig: https://docs.python.org/3.6/library/logging.config.html#logging-config-dictschema


Best practices
==============

Before you can test for rules, these rules must be registered with a rule set,
and for this to happen the modules containing your rule definitions must be
imported.

For complex projects with several predicates and rules, it may not be
practical to define all your predicates and rules inside one module. It might
be best to split them among any sub-components of your project. In a Django
context, these sub-components could be the apps for your project.

On the other hand, because importing predicates from all over the place in
order to define rules can lead to circular imports and broken hearts, it's
best to further split predicates and rules in different modules.

``rules`` may optionally be configured to autodiscover ``rules.py`` modules in
your apps and import them at startup. To have ``rules`` do so, just edit your
``INSTALLED_APPS`` setting:

.. code:: python

    INSTALLED_APPS = (
        # replace 'rules' with:
        'rules.apps.AutodiscoverRulesConfig',
    )

**Note:** On Python 2, you must also add the following to the top of your
``rules.py`` file, or you'll get import errors trying to import ``rules``
itself:

.. code:: python

    from __future__ import absolute_import


API Reference
=============

The core APIs are accessible from the root ``rules`` module. Django-specific
functionality for the Admin and views is available from ``rules.contrib``.


Class ``rules.Predicate``
-------------------------

You create ``Predicate`` instances by passing in a callable:

.. code:: python

    >>> def is_book_author(user, book):
    ...     return book.author == user
    ...
    >>> pred = Predicate(is_book_author)
    >>> pred
    <Predicate:is_book_author object at 0x10eeaa490>

You may optionally provide a different name for the predicate that is used
when inspecting it:

.. code:: python

    >>> pred = Predicate(is_book_author, name='another_name')
    >>> pred
    <Predicate:another_name object at 0x10eeaa490>

Also, you may optionally provide ``bind=True`` in order to be able to access
the predicate instance with ``self``:

.. code:: python

    >>> def is_book_author(self, user, book):
    ...     if self.context.args:
    ...         return user == book.author
    ...     return False
    ...
    >>> pred = Predicate(is_book_author, bind=True)
    >>> pred
    <Predicate:is_book_author object at 0x10eeaa490>


Instance methods
++++++++++++++++

``test(obj=None, target=None)``
    Returns the result of calling the passed in callable with zero, one or two
    positional arguments, depending on how many it accepts.


Class ``rules.RuleSet``
-----------------------

``RuleSet`` extends Python's built-in `dict`_ type. Therefore, you may create
and use a rule set any way you'd use a dict.

.. _dict: http://docs.python.org/library/stdtypes.html#mapping-types-dict


Instance methods
++++++++++++++++

``add_rule(name, predicate)``
    Adds a predicate to the rule set, assigning it to the given rule name.
    Raises ``KeyError`` if another rule with that name already exists.

``set_rule(name, predicate)``
    Set the rule with the given name, regardless if one already exists.

``remove_rule(name)``
    Remove the rule with the given name. Raises ``KeyError`` if a rule with
    that name does not exist.

``rule_exists(name)``
    Returns ``True`` if a rule with the given name exists, ``False`` otherwise.

``test_rule(name, obj=None, target=None)``
    Returns the result of calling ``predicate.test(obj, target)`` where
    ``predicate`` is the predicate for the rule with the given name. Returns
    ``False`` if a rule with the given name does not exist.

Decorators
----------

``@predicate``
    Decorator that creates a predicate out of any callable:

    .. code:: python

        >>> @predicate
        ... def is_book_author(user, book):
        ...     return book.author == user
        ...
        >>> is_book_author
        <Predicate:is_book_author object at 0x10eeaa490>

    Customising the predicate name:

    .. code:: python

        >>> @predicate(name='another_name')
        ... def is_book_author(user, book):
        ...     return book.author == user
        ...
        >>> is_book_author
        <Predicate:another_name object at 0x10eeaa490>

    Binding ``self``:

    .. code:: python

        >>> @predicate(bind=True)
        ... def is_book_author(self, user, book):
        ...     if 'user_has_special_flag' in self.context:
        ...         return self.context['user_has_special_flag']
        ...     return book.author == user


Predefined predicates
---------------------

``always_allow()``, ``always_true()``
    Always returns ``True``.

``always_deny()``, ``always_false()``
    Always returns ``False``.

``is_authenticated(user)``
    Returns the result of calling ``user.is_authenticated()``. Returns
    ``False`` if the given user does not have an ``is_authenticated`` method.

``is_superuser(user)``
    Returns the result of calling ``user.is_superuser``. Returns ``False``
    if the given user does not have an ``is_superuser`` property.

``is_staff(user)``
    Returns the result of calling ``user.is_staff``. Returns ``False`` if the
    given user does not have an ``is_staff`` property.

``is_active(user)``
    Returns the result of calling ``user.is_active``. Returns ``False`` if the
    given user does not have an ``is_active`` property.

``is_group_member(*groups)``
    Factory that creates a new predicate that returns ``True`` if the given
    user is a member of *all* the given groups, ``False`` otherwise.


Shortcuts
---------

Managing the shared rule set
++++++++++++++++++++++++++++

``add_rule(name, predicate)``
    Adds a rule to the shared rule set. See ``RuleSet.add_rule``.

``set_rule(name, predicate)``
    Set the rule with the given name from the shared rule set. See
    ``RuleSet.set_rule``.

``remove_rule(name)``
    Remove a rule from the shared rule set. See ``RuleSet.remove_rule``.

``rule_exists(name)``
    Returns whether a rule exists in the shared rule set. See
    ``RuleSet.rule_exists``.

``test_rule(name, obj=None, target=None)``
    Tests the rule with the given name. See ``RuleSet.test_rule``.


Managing the permissions rule set
+++++++++++++++++++++++++++++++++

``add_perm(name, predicate)``
    Adds a rule to the permissions rule set. See ``RuleSet.add_rule``.

``set_perm(name, predicate)``
    Replace a rule from the permissions rule set. See ``RuleSet.set_rule``.

``remove_perm(name)``
    Remove a rule from the permissions rule set. See ``RuleSet.remove_rule``.

``perm_exists(name)``
    Returns whether a rule exists in the permissions rule set. See
    ``RuleSet.rule_exists``.

``has_perm(name, user=None, obj=None)``
    Tests the rule with the given name. See ``RuleSet.test_rule``.


Licence
=======

``django-rules`` is distributed under the MIT licence.

Copyright (c) 2014 Akis Kesoglou

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
