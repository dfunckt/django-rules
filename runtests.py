#!/usr/bin/env python

import sys
from os import environ
from os.path import abspath, dirname, join

import nose


def main():
    project_dir = dirname(abspath(__file__))

    # setup path
    sys.path.insert(0, project_dir)  # project dir
    sys.path.insert(0, join(project_dir, 'tests'))  # tests dir

    environ['DJANGO_SETTINGS_MODULE'] = 'testapp.settings'

    try:
        # django >= 1.7
        from django import setup
    except ImportError:
        pass
    else:
        setup()

    # setup test env
    from django.test.utils import setup_test_environment
    setup_test_environment()

    # setup db
    from django.core.management import call_command, CommandError
    options = {
        'interactive': False,
        'verbosity': 1,
    }
    try:
        call_command('migrate', **options)
    except CommandError:  # Django < 1.7
        call_command('syncdb', **options)

    # run tests
    return nose.main()


if __name__ == '__main__':
    main()
