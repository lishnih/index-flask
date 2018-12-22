#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-29

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
import os
import re
import glob
import logging

from sqlalchemy.types import TypeDecorator, String

from ..app import db
from .model import Model


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


class StrType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return str(value)


def check_model(aModel):
    if hasattr(aModel, '__rev__'):
        model = db.session.query(Model).filter_by(name=aModel.__tablename__).first()
        if model:
            if model.rev != aModel.__rev__:
                logging.warning("Revision of the model '{0}' changed: {1} -> {2}".\
                    format(aModel.__tablename__, model.rev, aModel.__rev__))

        else:
            model = Model(name=aModel.__tablename__, rev=aModel.__rev__)
            db.session.add(model)
            db.session.commit()

    else:
        logging.warning("Revision missed in the model: {0}".format(aModel.__tablename__))
