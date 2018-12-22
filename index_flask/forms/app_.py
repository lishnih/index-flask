#!/usr/bin/env python
# coding=utf-8
# Stan 2016-07-12

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import re

from wtforms import Form, SubmitField, StringField, validators

from ..models.app_ import App


class AddAppForm(Form):
    name = StringField('Name:', [
            validators.DataRequired(),
            validators.Length(min=6, max=40),
        ],
        render_kw={
            "placeholder": "App name (required)",
        }
    )
    description = StringField('Description:',
        render_kw={
            "placeholder": "Description (optional)",
        }
    )
    submit = SubmitField('Add')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if not re.match('[A-Za-z][\w\.]*', self.name.data):
            self.name.errors.append('All characters in the string must be alphanumeric or dot with underline')
            return False

        app = App.query.filter_by(name=self.name.data).first()
        if app:
            self.name.errors.append('App with the same name already registered')
            return False

        return True
