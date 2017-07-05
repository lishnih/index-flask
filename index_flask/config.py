#!/usr/bin/env python
# coding=utf-8

import os
basedir = os.path.abspath(os.path.dirname(__file__))
home = os.path.expanduser("~")

CSRF_ENABLED = True
SECRET_KEY = 'secret_\xfb+\x14-\xdf_\xbb=\x8f'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

# SQLALCHEMY_BINDS = {
#   'index':   'sqlite:///' + os.path.join(home, 'index.db'),
#   'appmeta': 'sqlite:////path/to/appmeta.db'
# }
