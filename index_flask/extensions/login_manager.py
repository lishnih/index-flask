#!/usr/bin/env python
# coding=utf-8
# Stan 2018-08-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request

from flask_login import LoginManager

from ..app import app
from ..models.user import User


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_signin'


@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email, active=True).first()
