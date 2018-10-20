#!/usr/bin/env python
# coding=utf-8
# Stan 2018-08-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)


# ===== Import Application and App DB =====
from .app import app, db


# ===== Create the tables =====
from .models import (user, app_, group, database, favorite, register, page,
                     sql_template, handler, source, source_task, module)

db.create_all()


# ===== Import extensions =====
from .extensions import *


# ===== Import views =====
from .core.load_modules import load_modules, require_ext

load_modules('views_user')
load_modules('views_db')
load_modules('views')
