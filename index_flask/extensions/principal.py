#!/usr/bin/env python
# coding=utf-8
# Stan 2018-08-02

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request

from flask_login import current_user
from flask_principal import (Principal, RoleNeed, UserNeed,
                             Identity, identity_loaded)

from ..app import app
from ..models.user import User


principal = Principal(app)


@principal.identity_loader
def load_identity_when_session_expires():
    if request.endpoint in ['static']:
        return

    if hasattr(current_user, 'id'):
        return Identity(current_user.id)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    if request.endpoint in ['static']:
        return

    if identity.id:
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        user = User.query.filter_by(id=identity.id, active=True).first()
        if user and hasattr(user, 'groups'):
            for i in user.groups:
                identity.provides.add(RoleNeed(i.name))
