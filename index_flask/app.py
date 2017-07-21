#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07, 2017-07-20

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import re

from flask import request

from flask_login import LoginManager, current_user
from flask_principal import ( Principal, RoleNeed, UserNeed,
                              Identity, identity_loaded )

from jinja2 import evalcontextfilter, Markup, escape

from .models import User
from .core.backwardcompat import *

from .a import app


##### login_manager #####

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()

# @login_manager.token_loader
# def my_token_loader(token):
#     return User.query.filter_by(token=token).first()


##### principal #####

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


##### filters #####

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = '\n\n'.join('<p>%s</p>' % p.replace('\n', '<br />\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


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
