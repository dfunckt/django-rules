django-rules
^^^^^^^^^^^^

.. image:: https://travis-ci.org/dfunckt/django-rules.svg?branch=master
    :target: https://travis-ci.org/dfunckt/django-rules
.. image:: https://coveralls.io/repos/dfunckt/django-rules/badge.png
    :target: https://coveralls.io/r/dfunckt/django-rules

``rules`` is a tiny but powerful app providing object-level permissions to
Django, without requiring a database. At its core, it is a generic framework
for building rule-based systems, similar to `decision trees`_. It can also be
used as a standalone library in other contexts and frameworks.

.. _decision trees: http://wikipedia.org/wiki/Decision_tree


Requirements
============

``rules`` requires Python 2.6/3.2 or newer. It can optionally integrate with
Django, in which case requires Django 1.5 or newer.


How to install
==============

Using pip::

    $ pip install rules

Manually::

    $ git clone https://github.com/dfunckt/django-rules.git
    $ cd django-rules
    $ python setup.py install


Using ``rules``
===============

``rules`` is based on the idea that you maintain a dict-like object that maps
string keys used as identifiers of some kind, to callables, called
*predicates*. This dict-like object is actually an instance of ``RuleSet`` and
the predicates are instances of ``Predicate``.


Creating predicates
-------------------

Let's ignore rule sets for a moment and go ahead and define a predicate. The
easiest way is with the ``@predicate`` decorator::

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
set. We can use the ``is_book_author`` predicate we defined earlier::

    >>> rules.add_rule('can_edit_book', is_book_author)
    >>> rules.add_rule('can_delete_book', is_book_author)

Assuming we've got some data, we can now test our rules::

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
    predicates return ``True``, otherwise ``False``.
*   ``P1 | P2``: Returns a new predicate that returns ``True`` if *any* of the
    predicates returns ``True``, otherwise ``False``.
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
will come in handy::

    >>> is_editor = rules.is_group_member('editors')
    >>> is_editor
    <Predicate:is_group_member:editors object at 0x10eee1350>

We could combine it with the ``is_book_author`` predicate to create a new one
that checks for either condition::

    >>> is_book_author_or_editor = is_book_author | is_editor
    >>> is_book_author_or_editor
    <Predicate:(is_book_author | is_group_member:editors) object at 0x10eee1390>

We can now update our ``can_edit_book`` rule::

    >>> rules.add_rule('can_edit_book', is_book_author_or_editor)
    Traceback (most recent call last):
        ...
    KeyError: A rule with name `can_edit_book` already exists
    >>> rules.remove_rule('can_edit_book')
    >>> rules.add_rule('can_edit_book', is_book_author_or_editor)
    >>> rules.test_rule('can_edit_book', adrian, guidetodjango)
    True
    >>> rules.test_rule('can_delete_book', adrian, guidetodjango)
    True

Let's see what happens with another user::

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

Using ``rules`` with Django
===========================

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
and ``books.delete_book`` permissions::

    >>> rules.add_perm('books.change_book', is_book_author | is_editor)
    >>> rules.add_perm('books.delete_book', is_book_author)

See the difference in the API? ``add_perm`` adds to a permissions-specific
rule set, whereas ``add_rule`` adds to a default shared rule set. It's
important to know however, that these two rule sets are separate, meaning that
adding a rule in one does not make it available to the other.


Checking for permission
+++++++++++++++++++++++

Let's go ahead and check whether ``adrian`` has change permission to the
``guidetodjango`` book::

    >>> adrian.has_perm('books.change_book', guidetodjango)
    False

When you call the ``User.has_perm`` method, Django asks each backend in
``settings.AUTHENTICATION_BACKENDS`` whether a user has the given permission
for the object. When queried for object permissions, Django's default
authentication backend always returns ``False``. ``rules`` comes with an
authorization backend, that is able to provide object-level permissions by
looking into the permissions-specific rule set.

Let's add the ``rules`` authorization backend in settings::

    AUTHENTICATION_BACKENDS = (
        'rules.permissions.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

Now, checking again gives ``adrian`` the required permissions::

    >>> adrian.has_perm('books.change_book', guidetodjango)
    True
    >>> adrian.has_perm('books.delete_book', guidetodjango)
    True
    >>> martin.has_perm('books.change_book', guidetodjango)
    True
    >>> martin.has_perm('books.delete_book', guidetodjango)
    False


Rules and permissions in templates
----------------------------------

``rules`` comes with two template tags to allow you to test for rules and
permissions in templates.

Add ``rules`` to your ``INSTALLED_APPS``::

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


Custom rule sets
================

You may create as many rule sets as you need::

    >>> features = rules.RuleSet()

And manipulate them by adding, removing, querying and testing rules::

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

If using Django 1.7 and later, ``rules`` may optionally be configured to
autodiscover ``rules.py`` modules in your apps and import them at startup. To
have ``rules`` do so, just edit your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # ...
        'rules.apps.AutodiscoverRulesConfig',
    )


API Reference
=============

Everything is accessible from the root ``rules`` module.


Class ``rules.Predicate``
-------------------------

You create ``Predicate`` instances by passing in a callable::

    >>> def is_book_author(user, book):
    ...     return book.author == user
    ...
    >>> pred = Predicate(is_book_author)
    >>> pred
    <Predicate:is_book_author object at 0x10eeaa490>

You may optionally provide a different name for the predicate that is used
when inspecting it::

    >>> pred = Predicate(is_book_author, name='another_name')
    >>> pred
    <Predicate:another_name object at 0x10eeaa490>


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
    Decorator that creates a predicate out of any callable::
    
        >>> @predicate
        ... def is_book_author(user, book):
        ...     return book.author == user
        ...
        >>> is_book_author
        <Predicate:is_book_author object at 0x10eeaa490>

    Customising the predicate name::
    
        >>> @predicate(name='another_name')
        ... def is_book_author(user, book):
        ...     return book.author == user
        ...
        >>> is_book_author
        <Predicate:another_name object at 0x10eeaa490>


Predefined predicates
---------------------

``always_allow()``
    Always returns ``True``.

``always_deny()``
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

``remove_perm(name)``
    Remove a rule from the permissions rule set. See ``RuleSet.remove_rule``.

``perm_exists(name)``
    Returns whether a rule exists in the permissions rule set. See
    ``RuleSet.rule_exists``.

``has_perm(name, user=None, obj=None)``
    Tests the rule with the given name. See ``RuleSet.test_rule``.
