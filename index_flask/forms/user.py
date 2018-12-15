#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from wtforms import (Form, SubmitField, StringField, PasswordField,
                     HiddenField, BooleanField, validators)

from ..app import bcrypt
from ..models.user import User


class RegistrationForm(Form):
    name = StringField('Name:', [
            validators.DataRequired(),
            validators.Length(min=3, max=128),
        ],
        render_kw={
            "placeholder": "Your name (required)",
        }
    )
    email = StringField('Email', [
            validators.DataRequired(),
            validators.Length(min=6, max=128),
        ],
        render_kw={
            "placeholder": "Your email (required)",
        }
    )
    password = PasswordField('New password', [
            validators.DataRequired(),
            validators.Length(min=6),
        ],
        render_kw={
            "placeholder": "Password (required)",
        }
    )
    confirm = PasswordField('Confirm password', [
            validators.DataRequired(),
            validators.EqualTo('password', message='Passwords must match'),
        ],
        render_kw={
            "placeholder": "Password (required)",
        }
    )
    format = StringField()
    submit = SubmitField('Sign up')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data, active=False).first()
        if user:
            self.email.errors.append('This account deleted! You can <a href="recover">recover</a> the profile!')
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('Email is already in use!')
            return False

        return True


class LoginForm(Form):
    email = StringField('Email', [
            validators.Required(),
        ],
        render_kw={
            "placeholder": "Your email",
        }
    )
    password = PasswordField('Password', [
            validators.Required(),
        ],
        render_kw={
            "placeholder": "Your password",
        }
    )
    remember = BooleanField('Remember me')
    format = StringField()
    submit = SubmitField('Sign in')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data, active=True).first()
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
        ],
        render_kw={
            "placeholder": "Password (required)",
        }
    )
    password = PasswordField('New password', [
            validators.DataRequired(),
            validators.Length(min=6),
        ],
        render_kw={
            "placeholder": "Password (required)",
        }
    )
    confirm = PasswordField('Confirm password', [
            validators.DataRequired(),
            validators.EqualTo('password', message='Passwords must match'),
        ],
        render_kw={
            "placeholder": "Password (required)",
        }
    )
    format = StringField()
    submit = SubmitField('Change password')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(email=self.email.data, active=True).first()
        if not user:
            self.current.errors.append("User doesn't exist")
            return False

        current = user.get_password(self.current.data)
        if current != user.password:
            self.current.errors.append('Invalid password')
            return False

        self.user = user
        return True
