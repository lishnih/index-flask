#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-11

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os
from datetime import datetime

from flask import jsonify

from .core.backwardcompat import *
from .models import db, Module
from . import app


def load_modules(folder):
    base = app.name
    basedir = app.root_path

    ldir = os.listdir('{0}/{1}/'.format(basedir, folder))
    for i in ldir:
        ext_name, ext = os.path.splitext(i)
        if ext == '.py' and ext_name != '__init__':
            name = '{0}.{1}.{2}'.format(base, folder, ext_name)

            module = Module.query.filter_by(name=ext_name, folder=folder).first()
            if not module:
                module = Module(ext_name, folder)
                db.session.add(module)
                db.session.commit()

            if module.active:
                try:
                    __import__(name, globals(), locals(), [])
                    module.loaded = datetime.utcnow()
                    module.error = ''
                except Exception, e:
                    message = "Error: ".format(e.message)
                    print(e, '>', folder, ext_name, base, basedir)
                    module.error = message

                db.session.commit()


def require_ext(ext_name, response=None):
    base = app.name
    folder = 'extensions'

    name = '{0}.{1}.{2}'.format(base, folder, ext_name)
    mod = sys.modules.get(name)
    if mod:
        return mod

    msg = "Отсутствует модуль '{0}'".format(ext_name)
    if response == 'html':
        return msg
    if response == 'json':
        return jsonify(result="error", message=msg)
