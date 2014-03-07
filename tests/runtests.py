#!/usr/bin/env python

from os import environ
from os.path import abspath, dirname

import nose


def main():
    try:
        import rules
    except ImportError as e:
        if str(e) not in ("No module named 'rules'", "No module named rules"):
            raise
        else:
            repo_dir = dirname(dirname(abspath(__file__)))
            environ['NOSE_WHERE'] = repo_dir
    return nose.main()


if __name__ == '__main__':
    main()
