#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_login import current_user

from wtforms import Form, StringField, HiddenField, SubmitField, validators

from ..models.source import Source


class AddSourceForm(Form):
    name = StringField('Name:', [
            validators.DataRequired(),
        ],
        render_kw={
            "placeholder": "Source name (required)",
        }
    )
    path = StringField('Path:', [
            validators.DataRequired(),
        ],
        render_kw={
            "id": "path",
        }
    )
    path_id = HiddenField('',
        render_kw={
            "id": "path_id",
        }
    )
    provider = HiddenField('',
        render_kw={
            "id": "provider",
        }
    )
    submit = SubmitField('Append')

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        source = Source.query.filter_by(_user_id=current_user.id, name=self.name.data).first()
        if source:
            self.name.errors.append('Source name already registered!')
            return False

        return True
