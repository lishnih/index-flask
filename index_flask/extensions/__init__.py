#!/usr/bin/env python
# coding=utf-8
# Stan 2018-08-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
import os
import re
import glob
import logging


py_version = sys.version_info[:2]
PY2 = py_version[0] == 2
logging.debug("Python: {0}".format(py_version))


files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "*.py")))
modules = [os.path.basename(i)[:-3] for i in files if not i.endswith("__init__.py")]

pattern = re.compile("[_A-Za-z][_A-Za-z0-9]*$")
for i in modules:
    if not pattern.match(i):
        logging.warning("Wrong module name, skipping: {0!r}".format(i))
        del modules[modules.index(i)]

for i in modules:
    logging.debug("Module: {0}".format(i))


if PY2:
    modules = [i.encode('utf-8') for i in modules]


__all__ = modules
