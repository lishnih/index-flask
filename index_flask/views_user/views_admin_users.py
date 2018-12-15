#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-28

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import request, jsonify, redirect, flash
from jinja2 import Markup, escape

from flask_login import login_required
from flask_principal import Permission, RoleNeed

from ..app import app, db
from ..core.functions import get_next
from ..core.load_modules import is_loaded
from ..core.render_response import render_ext
from ..forms.user import RegistrationForm
from ..models.user import User


# ===== Roles =====

admin_permission = Permission(RoleNeed('admin'))


# ===== Routes =====

@app.route('/admin/')
@login_required
@admin_permission.require(403)
def admin():
    return render_ext('admin/index.html',
             title = 'Admin page',
           )


@app.route('/admin/users')
@login_required
@admin_permission.require(403)
def admin_users():
    s = User.query
    users = s.all()
    total = s.count()

    names = [i.name for i in User.__table__.c]
    rows = []
    for user in users:
        row = []
        for i in names:
            if i == 'email':
                row.append(Markup('<a href="user/{0}">{0}</a>'.format(escape(user.email))))
            else:
                row.append(user.__dict__.get(i))

        rows.append(row)

    return render_ext('base.html',
             title = 'Users',
             names = names,
             rows = rows,
             total = total,
           )


@app.route('/admin/user/<email>')
@login_required
@admin_permission.require(403)
def admin_user(email):
    user = User.query.filter_by(email=email).first()

    names = [i.name for i in User.__table__.c]
    rows = [[user.__dict__.get(i) for i in names]]

    return render_ext('base.html',
             title = 'User',
             names = names,
             rows = rows,
           )


@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_add_user():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username = form.email.data,
            email = form.email.data,
            password = form.password.data,
            name = form.name.data,
        )
        db.session.add(user)
        db.session.commit()

        user.init_env()

        flash('User added!')
        return redirect(get_next('admin'))

    return render_ext('user/signup.html',
             title = 'Registering new user',
             form = form,
             next = request.args.get('next', '/admin/'),
           )
