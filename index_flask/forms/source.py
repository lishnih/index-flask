#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_login import current_user

from wtforms import Form, StringField, HiddenField, BooleanField, validators

from ..models.source import Source


class AddSourceForm(Form):
    name = StringField('Name *', [validators.Required()])
    path = StringField('Path', [validators.Required()], id='path')
    path_id = HiddenField('', id='path_id')
    provider = HiddenField('', id='provider')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        source = Source.query.filter_by(_user_id=current_user.id, name=self.name.data).first()
        if source:
            self.name.errors.append('Source name already registered!')
            return False

        return True
