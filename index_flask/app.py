#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import logging

from flask import Flask

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
# from flask_migrate import Migrate


app = Flask(__name__, static_url_path='')

from . import config
app.config.from_object(config)


if 'INDEX_CONFIG' in app.config:
    logging.debug("Config file '{0}' loading...".format(app.config['INDEX_CONFIG']))
    try:
        app.config.from_pyfile(app.config['INDEX_CONFIG'])
    except:
        logging.warning("Config file '{0}' not loaded".format(app.config['INDEX_CONFIG']))


# Flask-Bcrypt, Flask-SQLAlchemy, Flask-Mail
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
mail = Mail(app)
# migrate = Migrate(app, db)


# Celery
if app.config.get('CELERY_ENABLED'):
    try:
        from celery import Celery

        celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
        celery.conf.update(app.config)

    except Exception as e:
        logging.exception("Error while initializing Celery '{0}'".format(e))
        app.config['CELERY_ENABLED'] == False


# Yandex Database
if app.config.get('YDB_ENABLED'):
    try:
        from .core.ydb_driver import start

        ydb = start()

    except Exception as e:
        logging.exception("Error while initializing Yandex Database '{0}'".format(e))
        app.config['YDB_ENABLED'] == False
