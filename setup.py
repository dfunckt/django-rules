#!/usr/bin/env python
from os.path import dirname, join

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from rules import VERSION


def get_version(version):
    """
    Returns a PEP 386-compliant version number from ``version``.
    """
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


with open(join(dirname(__file__), 'README.rst')) as f:
    long_description = f.read()


setup(
    name='rules',
    description='Awesome Django authorization, without the database',
    version=get_version(VERSION),
    long_description=long_description,

    url='http://github.com/dfunckt/django-rules',
    author='Akis Kesoglou',
    author_email='akiskesoglou@gmail.com',
    maintainer='Akis Kesoglou',
    maintainer_email='akiskesoglou@gmail.com',
    license='MIT',

    zip_safe=False,
    packages=[
        'rules',
        'rules.templatetags',
        'rules.contrib',
        'rules.compat',
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
