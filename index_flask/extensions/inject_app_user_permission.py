#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_login import current_user
from flask_principal import Permission, RoleNeed

from ..app import app


@app.context_processor
def inject_app_root():
    admin_permission = Permission(RoleNeed('admin'))
    debug_permission = Permission(RoleNeed('debug'))
    statistics_permission = Permission(RoleNeed('statistics'))

    return dict(
        name = None if current_user.is_anonymous else \
               current_user.name or current_user.email,
        p_admin = admin_permission.can(),
        p_debug = debug_permission.can(),
        p_statistics = statistics_permission.can(),
    )
