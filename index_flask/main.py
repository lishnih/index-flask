#!/usr/bin/env python
# coding=utf-8
# Stan 2018-08-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)


# ===== Import Application and App DB =====
from .app import app, db


# ===== Import models and create tables =====
from .models import check_model
from .models import *

db.create_all(bind='__all__')

for c in db.Model._decl_class_registry.values():
    if hasattr(c, '__tablename__'):
        check_model(c)


# ===== Import extensions =====
from .extensions import *


# ===== Import views =====
from .core.load_modules import load_modules, require_ext

load_modules('views_user')
load_modules('views_db')
load_modules('views')
