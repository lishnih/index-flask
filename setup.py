#!/usr/bin/env python
# coding=utf-8

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from index_flask import (__pkgname__, __description__, __version__,
                         PY2, py_version)

import sys
import os
from setuptools import setup, find_packages

if PY2:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, the package requires Python 2.6 or better')
else:
    if py_version < (3, 3):
        raise RuntimeError('On Python 3, the package requires Python 3.3 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''


data_files = []

start_point = os.path.join(__pkgname__, 'static')
for root, dirs, files in os.walk(start_point):
    data_files.append((root, [os.path.join(root, i) for i in files]))

start_point = os.path.join(__pkgname__, 'templates')
for root, dirs, files in os.walk(start_point):
    data_files.append((root, [os.path.join(root, i) for i in files]))


if __name__ == '__main__':
    setup(
        name=__pkgname__,
        description=__description__,
        version=__version__,
        long_description=README,

        author='Stan',
        author_email='lishnih@gmail.com',
        url='https://github.com/lishnih/index-flask',
        platforms=['any'],
        keywords=['flask', 'indexing', 'reporting', 'documents'],

        packages=find_packages(),
        # ['index_flask', 'index_flask.core', 'index_flask.extensions',
        #  'index_flask.views', 'index_flask.view_j2']
#       include_package_data=True,
#       zip_safe=False,

#       package_data={__pkgname__: []},
        data_files=data_files,

        scripts=[
            'index_flask-initialize.py',
            'index_flask-standalone.py',
        ],

        install_requires=[
            'wtforms',
            'flask_login',
            'flask_principal',
            'flask_bcrypt',
            'flask_sqlalchemy',
            'flask_migrate',
            'social-auth-app-flask-sqlalchemy',
            'markdown',
            'dropbox',
            'yadisk',
            'python-docx',
#           'pyOpenSSL',
        ],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Flask',
            'Intended Audience :: Manufacturing',
            'License :: OSI Approved :: MIT License',
            'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
            'Natural Language :: Russian',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 3.3',
            'Topic :: Database',
            'Topic :: Utilities',
        ],
    )
