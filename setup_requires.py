#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
import pkg_resources
from subprocess import call

from setup import install_requires as packages

print(sys.version)

for i, j in enumerate(packages, 1):
    print(i, j)

call("python -m pip install --upgrade " + ' '.join(packages), shell=True)
