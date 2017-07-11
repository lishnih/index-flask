#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os

from flask import session, request, render_template, redirect, flash

from flask_login import login_required, login_user, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed

from .core.backwardcompat import *
from .core.db import getDbList
# from .core.dump_html import html
from .models import db, User
from .forms import RegistrationForm, LoginForm

from . import app, get_next


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    if not current_user.is_anonymous:
        return render_template('user/logout.html',
                 title = 'Logout',
                 name = current_user.name,
                 next = "/register",
               )

    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            email = form.email.data,
            username = form.username.data,
            name = form.name.data,
            company = form.company.data,
            password = form.password.data,
        )
        db.session.add(user)
        db.session.commit()

        flash('Thanks for registering')
        return redirect(get_next('/login'))

    return render_template('user/register.html',
             title = 'Registering new user',
             form = form,
             next = request.args.get('next', '/login'),
           )


@app.route('/login', methods=['GET', 'POST'])
def user_login(user=None):
    if not current_user.is_anonymous:
        return render_template('user/logout.html',
                 title = 'Logout',
                 name = current_user.name,
                 next = "/login",
               )

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user(form.user, remember=form.remember.data)

        identity_changed.send(app, identity=Identity(form.user.id))

        flash('Successfully logged in as {0}'.format(form.user.name))
        return redirect(get_next())

    return render_template('user/login.html',
             title = 'Login',
             form = form,
             next = request.args.get('next', '/'),
           )


@app.route("/confirm/<code>")
def user_confirm(code=None):
    # log request...

    user = User.query.filter_by(verified=code).first()
    if user:
        status = 'verified'
        user.verified = ''
        db.session.commit()
    else:
        status = 'not verified'

    return render_template('user/confirm.html',
             title = 'Confirm email',
             status = status,
           )


@app.route("/logout")
@login_required
def user_logout():
    logout_user()

    for key in ('identity.id', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(app, identity=AnonymousIdentity())

    return redirect(get_next())


@app.route("/profile")
@login_required
def user_profile():
#   return html(current_user)

    return render_template('user/profile.html',
             title = 'Profile',
             cu = current_user,
             groups = current_user.groups,
             databases = current_user.databases,
             verified = 'not verified' if current_user.verified else 'verified'
           )


@app.route("/edit", methods=['GET', 'POST'])
@login_required
def user_edit():
    return render_template('user/edit.html',
             title = 'Edit profile',
             cu = current_user,
           )


@app.route("/append_db")
@login_required
def user_append_db():
    dbpath = os.path.expanduser("~/.config/index/{0}".format(current_user.username))
    dbs_list = getDbList(current_user.home)

    return render_template('dump_list.html',
             obj = dbs_list,
           )


@app.route("/init_env")
@login_required
def user_init_env():
    current_user.init_env()
    db.session.commit()

    flash("Task 'Init environment' executed!")
    return redirect(get_next('/profile'))


@app.route("/send_verification")
@login_required
def user_send_verification():
    current_user.send_verification()

    flash("Task 'Send verification' executed!")
    return redirect(get_next('/profile'))


@app.route("/delete_account")
@login_required
def user_delete():
    return render_template('user/delete_account.html',
             title = 'Delete account',
             name = current_user.name,
           )
