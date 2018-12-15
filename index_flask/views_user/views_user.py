#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import session, request, redirect, url_for

from flask_login import login_required, login_user, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed

from ..app import app, db
from ..core.functions import get_next
from ..core.render_response import render_ext
from ..forms.user import RegistrationForm, LoginForm, ChangePasswordForm
from ..models.user import User


# ===== Routes =====

@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    form = RegistrationForm(request.form)
    message = None

    if not current_user.is_anonymous:
        return render_ext('user/logout.html',
            title = 'Logout',
            message = ("Already logged!", 'warning'),
            next = url_for('user_signup'),
        )

    if request.method == 'POST':
        if form.validate():
            user = User(
                username = form.email.data,
                email = form.email.data,
                password = form.password.data,
                name = form.name.data,
            )
            db.session.add(user)
            db.session.commit()

            login_user(user)
            identity_changed.send(app, identity=Identity(user.id))

            user.init_env()

            return render_ext("base.html",
                default = redirect(get_next()),
                message = "Thank you for registering!",
            )

        else:
            message = "Invalid data!", 'warning'

    return render_ext('user/signup.html',
        title = 'Registering new user',
        message = message,
        form = form,
    )


@app.route('/signin', methods=['GET', 'POST'])
def user_signin(user=None):
    form = LoginForm(request.form)
    message = None

    if not current_user.is_anonymous:
        return render_ext('user/logout.html',
            title = 'Logout',
            message = ("Already logged!", 'warning'),
            next = url_for('user_signin'),
        )

    if request.method == 'POST':
        if form.validate():
            login_user(form.user, remember=form.remember.data)
            identity_changed.send(app, identity=Identity(form.user.id))

            return render_ext("base.html",
                default = redirect(get_next()),
                message = "Successfully logged in as {0}".format(form.user.name),
            )

        else:
            message = "Invalid data!", 'warning'

    return render_ext('user/signin.html',
        title = 'Sign in',
        message = message,
        form = form,
    )


@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def user_change_password():
    form = ChangePasswordForm(request.form)
    message = None

    if request.method == 'POST':
        if form.validate():
            form.user.change_password(form.password.data)
            db.session.commit()

            return render_ext("base.html",
                default = redirect(get_next()),
                message = "Successfully changed password!",
            )

        else:
            message = ("Invalid data!", 'warning'),

    return render_ext('user/change_password.html',
        title = 'Change Password',
        message = message,
        form = form,
        next = url_for('user_profile'),
    )


@app.route("/confirm/<code>", methods=['GET', 'POST'])
def user_confirm(code=None):
    user = User.query.filter_by(verified=code, active=True).first()
    if user:
        status = 'verified'
        user.set_verified()
        db.session.commit()

    else:
        status = 'not verified'

    return render_ext('user/confirm.html',
        title = 'Confirm email',
        format = 'json' if request.method == 'POST' else None,
        status = status,
    )


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def user_logout():
    logout_user()

    for key in ('identity.id', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(app, identity=AnonymousIdentity())

    return render_ext("base.html",
        default = redirect(get_next()),
        format = 'json' if request.method == 'POST' else None,
        message = "Successfully logged out!",
    )


@app.route("/delete", methods=['GET', 'POST'])
@login_required
def user_delete():
    current_user.active = False
    db.session.commit()

    user_logout()
    session.pop('_flashes', None)

    return render_ext("base.html",
        default = redirect(get_next(back=True)),
        format = 'json' if request.method == 'POST' else None,
        message = "Successfully deleted!",
    )


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def user_profile():
    return render_ext('user/profile.html',
        title = 'Profile',
        format = 'json' if request.method == 'POST' else None,
        user = current_user,
        groups = current_user.groups,
        verified = 'verified' if current_user.is_verified else 'not verified',
        name = current_user.name,   # Переменная для json запроса
    )


@app.route("/edit", methods=['GET', 'POST'])
@login_required
def user_edit():
    return render_ext('user/edit.html',
        title = 'Edit profile',
        user = current_user,
    )


@app.route("/logged", methods=['GET', 'POST'])
def user_logged():
    return render_ext("base.html",
        title = 'Status info',
        format = 'json' if request.method == 'POST' else None,
        message = "Not logged!" if current_user.is_anonymous else "Logged!",
        name = '' if current_user.is_anonymous else current_user.name,  # Переменная для json запроса
    )


@app.route("/send_verification", methods=['GET', 'POST'])
def user_send_verification():
    return render_ext("base.html",
        title = 'Status info',
        format = 'json' if request.method == 'POST' else None,
        message = "Not logged!" if current_user.is_anonymous else "Logged!",
        name = '' if current_user.is_anonymous else current_user.name,  # Переменная для json запроса
    )
