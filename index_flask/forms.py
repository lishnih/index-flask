#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from wtforms import (Form, StringField, PasswordField, HiddenField,
                     BooleanField, validators)

from .core.backwardcompat import *
from .models import User, Group


class RegistrationForm(Form):
    email = StringField('Email address *', [
        validators.Length(min=6, max=48),
    ])
    username = StringField('Username *', [
        validators.Length(min=6, max=32),
    ])
    name = StringField('Name *', [
        validators.Length(min=3),
    ])
    company = StringField('Company')
    password = PasswordField('New password *', [
        validators.Length(min=6),
    ])
    confirm = PasswordField('Repeat the password *', [
        validators.EqualTo('password', message='Passwords must match'),
    ])
    accept_tos = BooleanField('I accept the <a href="/tos.html">TOS</a>', [
        validators.DataRequired(),
    ])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('Email already registered')
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('Username already registered')
            return False

        return True


class LoginForm(Form):
    email = StringField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    remember = BooleanField('Remember me')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('Invalid email or password')
            self.password.errors.append('Invalid email or password')
            return False

        password = user.get_password(self.password.data)
        if password != user.password:
            self.email.errors.append('Invalid email or password')
            self.password.errors.append('Invalid email or password')
            return False

        self.user = user
        return True


class ChangePasswordForm(Form):
    username = HiddenField()
    current = PasswordField('Current password', [
        validators.Required(),
    ])
    password = PasswordField('New password', [
        validators.Length(min=6),
    ])
    confirm = PasswordField('Repeat the password', [
        validators.EqualTo('password', message='Passwords must match'),
    ])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.current.errors.append("User doesn't exist")
            return False

        current = user.get_password(self.current.data)
        if current != user.password:
            self.current.errors.append('Invalid password')
            return False

        self.user = user
        return True


class AddGroupForm(Form):
    name = StringField('Name *', [
        validators.Length(min=3, max=40),
    ])
    description = StringField('Description')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if not self.name.data.isalnum():
            self.name.errors.append('All characters in the string must be alphanumeric')
            return False

        group = Group.query.filter_by(name=self.name.data).first()
        if group:
            self.name.errors.append('Group already registered')
            return False

        return True
