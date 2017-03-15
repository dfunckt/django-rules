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

    from django import setup
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
    call_command('migrate', **options)

    # run tests
    return nose.main()


if __name__ == '__main__':
    main()
