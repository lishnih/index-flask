#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_principal import Principal, RoleNeed, UserNeed, identity_loaded

from .core.backwardcompat import *
from . import config


##### App #####

app = Flask(__name__, static_url_path='')
app.config.from_object(config)
# app.config.from_pyfile('app.cfg')


##### App DB and User #####

db = SQLAlchemy(app)

from .models import User


##### login_manager #####

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()

@login_manager.token_loader
def my_token_loader(token):
    return User.query.filter_by(token=token).first()


##### principals #####

principals = Principal(app)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if identity.id:
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        user = User.query.filter_by(id=identity.id).first()
        if user:
            for i in user.groups:
                identity.provides.add(RoleNeed(i.name))


##### get_next function #####

def get_next(default='/'):
    next = request.args.get('next')
    return next if next in [i.rule for i in app.url_map.iter_rules()] else \
           default


##### Import routes #####

from . import (
    views_index,  # Common views
    views_admin,  # Admin views
    views_user,   # User views
)


##### Import extensions and views #####

from .load_modules import load_modules, require_ext

load_modules('extensions')
load_modules('views')
