#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from .core.backwardcompat import *
from . import __pkgname__, config


# ===== App =====

app = Flask(__pkgname__, static_url_path='')
app.config.from_object(config)
# app.config.from_pyfile('app.cfg')


# ===== App's DB =====

db = SQLAlchemy(app)
