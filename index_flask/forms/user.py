#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from wtforms import (Form, StringField, PasswordField, HiddenField,
                     BooleanField, validators)

from ..app import bcrypt
from ..models.user import User


class RegistrationForm(Form):
    name = StringField('Name *', [
        validators.Length(min=3, max=128),
    ])
    email = StringField('Email *', [
        validators.Length(min=6, max=128),
    ])
    company = StringField('Company')
    password = PasswordField('New password *', [
        validators.Length(min=6),
    ])
    confirm = PasswordField('Confirm password *', [
        validators.EqualTo('password', message='Passwords must match'),
    ])
    accept_tos = BooleanField('I accept the <a href="p/tos">TOS</a>', [
        validators.DataRequired(),
    ])
    type = StringField()

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('Email is already in use!')
            return False

        return True


class LoginForm(Form):
    email = StringField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    remember = BooleanField('Remember me')
    type = StringField()

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('Invalid email or password!')
            self.password.errors.append('Invalid email or password!')
            return False

        if not bcrypt.check_password_hash(user.password, self.password.data):
            self.email.errors.append('Invalid email or password!')
            self.password.errors.append('Invalid email or password!')
            return False

        self.user = user
        return True


class ChangePasswordForm(Form):
    email = HiddenField()
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

        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.current.errors.append("User doesn't exist")
            return False

        current = user.get_password(self.current.data)
        if current != user.password:
            self.current.errors.append('Invalid password')
            return False

        self.user = user
        return True
