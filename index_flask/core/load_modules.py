#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-11

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import traceback
import logging
from datetime import datetime

from flask import jsonify

from ..app import app, db
from ..models.module import Module
from .types23 import *


# === Interface ===

root_pkg, _ = app.name.split('.', 1)
root_path = app.root_path
logging.debug(root_pkg)
logging.debug(root_path)


def load_modules(folder):
    ldir = os.listdir('{0}/{1}/'.format(root_path, folder))
    for i in ldir:
        ext_name, ext = os.path.splitext(i)
        if ext == '.py' and ext_name != '__init__':
            name = '{0}.{1}.{2}'.format(root_pkg, folder, ext_name)

            module = Module.query.filter_by(name=ext_name, folder=folder).first()
            if not module:
                module = Module(name=ext_name, folder=folder)
                db.session.add(module)
                db.session.commit()

            if module.active:
                try:
                    __import__(name, globals(), locals(), [])
                    module.loaded = datetime.utcnow()
                    module.error = ''

                except Exception as e:
                    tb_msg = traceback.format_exc()
                    message = "Error: {0!r}".format(e)
                    module.error = tb_msg
                    print(tb_msg)

                db.session.commit()


def require_ext(ext_name, response=None):
    folder = 'views'

    name = '{0}.{1}.{2}'.format(root_pkg, folder, ext_name)
    mod = sys.modules.get(name)
    if mod:
        return mod

    msg = "Отсутствует модуль '{0}'".format(ext_name)

    if response == 'json':
        return jsonify(result="error", message=msg)

    return msg


def is_loaded(ext_name, folder):
    name = '{0}.{1}.{2}'.format(root_pkg, folder, ext_name)
    mod = sys.modules.get(name)
    if mod:
        return True
