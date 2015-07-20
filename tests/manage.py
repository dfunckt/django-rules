#!/usr/bin/env python
import os
import sys

from os.path import abspath, dirname, join

if __name__ == "__main__":
    project_dir = dirname(dirname(abspath(__file__)))
    sys.path.insert(0, project_dir)
    sys.path.insert(0, join(project_dir, 'tests'))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
