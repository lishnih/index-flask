#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from wtforms import (Form, SubmitField, StringField, TextAreaField,
                     HiddenField, validators)

from ..models.group import Group


class AddGroupForm(Form):
    name = StringField('Name:', [
            validators.DataRequired(),
            validators.Length(min=3, max=40),
        ],
        render_kw={
            "placeholder": "Group name (required)",
        }
    )
    description = TextAreaField('Description:',
        render_kw={
            "placeholder": "Group description (optional)",
        }
    )
    format = StringField()
    submit = SubmitField('Add group')

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
