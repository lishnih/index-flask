#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, logging

from flask import ( current_app, session, request, redirect, url_for,
                    render_template, flash, abort )

from flask_login import ( LoginManager, login_required,
                          login_user, logout_user, current_user )

from flask_principal import ( Principal, Permission, RoleNeed, UserNeed,
                              Identity, AnonymousIdentity, identity_changed,
                              identity_loaded )

from werkzeug.local import LocalProxy

from .views_user_forms import RegistrationForm, LoginForm

from .ext.backwardcompat import *
from .ext.dump_html import html

from .models import User, db, append_user_to_group
from . import app, user_data


##### login_manager #####

login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(email):
    logging.debug('Loading user data... ({0})'.format(email))
    return User.query.filter_by(email=email).first()


@login_manager.token_loader
def my_token_loader(token):
    return User.query.filter_by(token=token).first()


##### identity_loaded #####

principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))


def _on_principal_init(sender, identity):
    if identity.id == 1:
        identity.provides.add(RoleNeed('admin'))


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


##### routes #####

@app.route('/admin')
# @admin_permission.require()
def user_admin():
    if not admin_permission.can():
        abort(403)

    return render_template('admin/admin.html',
             title = 'Admin page',
           )


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    if not current_user.is_anonymous:
        return render_template('user/logout.html',
                 title = 'Logout',
                 name = current_user.name,
                 next = "user_register",
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

        return redirect(url_for('user_login'))
    return render_template('user/register.html',
             title = 'Registering new user',
             form = form,
           )


@app.route('/login', methods=['GET', 'POST'])
# @app.route('/login/<user>', methods=['GET', 'POST'])
def user_login(user=None):
    if not current_user.is_anonymous:
        return render_template('user/logout.html',
                 title = 'Logout',
                 name = current_user.name,
                 next = "user_login",
               )

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user(form.user, remember=form.remember.data)

        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(form.user.id))

        flash('Successfully logged in as {0}'.format(form.user.name))

        next = request.args.get('next')
        if next and next in [rule.endpoint for rule in app.url_map.iter_rules()]:
            return redirect(url_for(next))

#       full_url = url_for("user_init_workspace", next=next)
        return redirect("/")

    return render_template('user/login.html',
             title = 'Login',
             form = form,
           )


@app.route("/confirm/<code>")
def user_confirm(code=None):
    # log request...
    print(code)

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

    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    next = request.args.get('next')
    if next and next in [rule.endpoint for rule in app.url_map.iter_rules()]:
        return redirect(url_for(next))

    return redirect("/")


@app.route("/profile")
@login_required
def user_profile():
#   return html(current_user)

    return render_template('user/profile.html',
             title = 'Profile',
             cu = current_user,
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
    return render_template('user/append_db.html',
             title = 'Append database',
             uid = current_user.id,
           )


@app.route("/init_env")
@login_required
def user_init_env():
    current_user.init_env()
    db.session.commit()

    flash("Task 'Init environment' executed!")

    next = request.args.get('next')
    if next and next in [rule.endpoint for rule in app.url_map.iter_rules()]:
        return redirect(url_for(next))

    return redirect(url_for('user_profile'))


@app.route("/send_verification")
@login_required
def user_send_verification():
    current_user.send_verification()

    flash("Task 'Send verification' executed!")

    next = request.args.get('next')
    if next and next in [rule.endpoint for rule in app.url_map.iter_rules()]:
        return redirect(url_for(next))

    return redirect(url_for('user_profile'))


@app.route("/delete_account")
@login_required
def user_delete():
    return render_template('user/delete_account.html',
             title = 'Delete account',
             name = current_user.name,
           )
