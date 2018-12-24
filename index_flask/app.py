#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import Flask

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
# from flask_migrate import Migrate

from celery import Celery

from . import config


app = Flask(__name__, static_url_path='')

app.config.from_object(config)
# app.config.from_pyfile('app.cfg')

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
mail = Mail(app)
# migrate = Migrate(app, db)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
