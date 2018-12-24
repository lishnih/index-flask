#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from wtforms import Form, StringField, HiddenField, BooleanField, validators

from ..models.database import Database


class AddDatabaseForm(Form):
    name = StringField('Name *', [validators.Required()])
    uri = StringField('URI *', [validators.Required()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        db = Database.query.filter_by(name=self.name.data).first()
        if db:
            self.name.errors.append('Name already registered!')
            return False

        return True
