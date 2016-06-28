#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, login_required, current_user

from flask_principal import ( Principal, Permission, RoleNeed, UserNeed,
                              identity_loaded )

from .ext.backwardcompat import *
from . import config


app = Flask(__name__, static_url_path='')
app.config.from_object(config)
# app.config.from_pyfile('app.cfg')


##### App db #####

db = SQLAlchemy(app)


##### login_manager #####

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'


@login_manager.user_loader
def load_user(email):
#   logging.debug('Loading user data... ({0})'.format(email))
    return models.User.query.filter_by(email=email).first()


@login_manager.token_loader
def my_token_loader(token):
    return models.User.query.filter_by(token=token).first()


##### principals #####

principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))
debug_permission = Permission(RoleNeed('debug'))


def _on_principal_init(sender, identity):
    if identity.id == 1:
        identity.provides.add(RoleNeed('admin'))
        identity.provides.add(RoleNeed('debug'))


identity_loaded.connect(_on_principal_init)


# @identity_loaded.connect_via(app)
# def on_identity_loaded(sender, identity):
#     identity.user = current_user
#
#     if hasattr(current_user, 'id'):
#         identity.provides.add(UserNeed(current_user.id))
#
#     if hasattr(current_user, 'roles'):
#         for role in current_user.roles:
#             identity.provides.add(RoleNeed(role.name))


##### get_next function #####

def get_next(default='/'):
    next = request.args.get('next')
    return next if next in [i.rule for i in app.url_map.iter_rules()] else \
           default


##### Import models and routes #####

from . import (
    models,       # Db Models
    view_j2,      # j2 package
    views,        # Common views
    views_admin,  # Admin views
    views_user,   # User views
    views_db,     # DB views
#   views_st,     # ST views
    views_debug,  # Debug views
)


##### j2 interface #####

@app.route("/j2", methods=["GET", "POST"])
@login_required
def j2():
    return jsonify(view_j2.view_j2(request))
