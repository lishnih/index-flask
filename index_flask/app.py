#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07, 2017-07-20

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request

from flask_login import LoginManager, current_user
from flask_principal import (Principal, RoleNeed, UserNeed,
                             Identity, identity_loaded)

from jinja2 import evalcontextfilter

from .core.backwardcompat import *
from .models import User

from .a import app


# ===== login_manager =====

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'


@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()


# @login_manager.token_loader
# def my_token_loader(token):
#     return User.query.filter_by(token=token).first()


# ===== principal =====

principal = Principal(app)


@principal.identity_loader
def load_identity_when_session_expires():
    if hasattr(current_user, 'id'):
        return Identity(current_user.id)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if identity.id:
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        user = User.query.filter_by(id=identity.id).first()
        if user:
            for i in user.groups:
                identity.provides.add(RoleNeed(i.name))


# ===== filters =====

@app.template_filter()
@evalcontextfilter
def safe_str(eval_ctx, value):
    if isinstance(value, string_types):
        if not isinstance(value, unicode):
            value = value.decode('utf8', 'ignore')

    elif not isinstance(value, all_types) and value is not None:
        try:
            value = str(value).decode('utf8', 'ignore')
        except:
            value = "[ {0} ]".format(type(value))

    return value


# ===== functions =====

def get_next(default='/'):
    next = request.args.get('next')
    return next if next in [i.rule for i in app.url_map.iter_rules()] else \
           default


def debug_query(query):
    try:
        return str(query)
    except Exception as e:
        return repr(query)


# ===== Import routes =====

from . import (
    views_index,  # Common views
    views_admin,  # Admin views
    views_user,   # User views
)


# ===== Import extensions and views =====

from .load_modules import load_modules, require_ext

load_modules('extensions')
load_modules('views')
