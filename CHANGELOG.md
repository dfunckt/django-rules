Changelog
=========

## v2.1.0 - 2019/08/11

- Added ability to automatically check for permissions in Drango Rest Framework
  viewsets.
- Added ability to automatically check for permissions in Drango class-based
  views.
- Added ability to automatically register permissions for models.
- Added shim for "six" in anticipation for Django 3.0 dropping support for
  Python 2 and removing "six" from its codebase.

## v2.0.1 - 2018/12/07

- Fixed issue with using ``rules`` in ``CreateView`` CBV

## v2.0.0 - 2018/07/22

- Removed support for Python 2.6 and 3.3
- Removed support for Django versions before 1.11
- Removed ``SkipPredicate`` exception and ``skip`` method of ``Predicate``
- Removed ``replace_rule`` and related APIs
- Added ``set_rule`` and related APIs to safely replace a rule without having
  to ensure one already exists
- Added compatibility with Django v2.1
- Re-introduced support for PyPy and PyPy 3
- Changed Python and Django supported versions policy to exclude end-of-life
  versions. Support for EOL'd versions will be dropped in minor version
  updates of ``rules`` from now on.

## v1.4.0 - 2018/07/21

- Fixed masking AttributeErrors raised from CBV get_object
- Fixed compatibility with `inspect` in newer Python 3 versions
- Added ability to replace rules and permissions

## v1.3.0 - 2017/12/13

- Added support for Django 2.0
- Added support for Django 1.11 and Python 3.6
- Dropped support for PyPy and PyPy3

## v1.2.1 - 2017/05/13

- Reverted "Fixed undesired caching in `is_group_member` factory"

## v1.2.0 - 2016/12/18

- Added logging to predicates
- Added support for Django 1.10
- Fixed undesired caching in `is_group_member` factory

## v1.1.1 - 2015/12/07

- Improved handling of skipped predicates

## v1.1.0 - 2015/12/05

- Fixed regression that wouldn't short-circuit boolean expressions
- Added support for Django 1.9 and Python 3.5
- Added support for skipping predicates simply by returning `None`.
  The previous way of skipping predicates by raising `SkipPredicate`
  has been deprecated and will not be supported in a future release.

## v1.0.0 - 2015/10/06

- Initial stable public release
- Dropped support for Python 3.2
- Added Django test suite
- Added function-based view decorator
- Added class-based view mixin

## v0.4 - 2015/02/16

- Added support for creating predicates from partial functions
- Added support for creating predicates from instance methods
- Added predicate invocation context
- Added support for automatically passing `self` to a predicate
- Added support for discarding a predicate's result

## v0.3 - 2014/10/15

- Added compatibility with PyPy and PyPy 3
- Added `always_true()` and `always_false()` predicates
- Added integration with Tox
- Bug fixes

## v0.2 - 2014/06/09

- Added compatibility with Python 3.4
- Improved admin integration

## v0.1 - 2014/03/07

- Initial public release
