#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, logging

from flask import ( request, render_template, redirect, url_for, abort, flash )

from flask_login import ( LoginManager, login_required,
                          login_user, logout_user, current_user )

from .views_user_forms import RegistrationForm, LoginForm

from .ext.backwardcompat import *
from .ext.dump_html import html

from .models import User, db
from . import app


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            email    = form.email.data,
            username = form.username.data,
            company  = form.company.data,
            password = form.password.data,
        )
        db.session.add(user)
        db.session.commit()

        flash('Thanks for registering')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
# @app.route('/login/<user>', methods=['GET', 'POST'])
def login(user=None):
    if not current_user.is_anonymous:
        return render_template('logout.html', username=current_user.username, next="login")

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_user(form.user, remember=form.remember.data)

        flash('Successfully logged in as {0}'.format(form.user.username))

        next = None
#       next = request.args.get('next')
#       if not next_is_valid(next):
#           return abort(400)

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()

    next = request.args.get('next')
    if next and next in [rule.endpoint for rule in app.url_map.iter_rules()]:
        return redirect(url_for(next))

    return redirect("/")


@app.route("/profile")
@login_required
def profile():
    return html(current_user)


# with app.test_client() as tc:
#     # login will set session cookie as well as remember me cookie
#     # User.get_auth_token will be called because we have defined a token_loader
#     tc.get('/login')
#
#     # clear the session cookie so the next request will use remember me
#     tc.cookie_jar.clear_session_cookies()
#
#     # our token_loader function should be called now as Flask-Login attempts to
#     # log us in with the remember me cookie
#     tc.get('/profile')
