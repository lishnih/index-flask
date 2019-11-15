#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-21

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_login import current_user

from wtforms import Form, StringField, SelectField, validators

from ..models.source import Source
from ..models.handler import Handler


class AddUserTaskForm(Form):
    source = SelectField('Source', [validators.Required()],
        render_kw={"class": "custom-select"}
    )
    handler = SelectField('Handler', [validators.Required()],
        render_kw={"class": "custom-select"}
    )
    handling = SelectField('Handling', [validators.Required()],
        choices=[['auto', 'Auto'], ['manual', 'Manual']],
        render_kw={"class": "custom-select"}
    )

    def __init__(self, form, sources, handlers, **kargs):
        super(AddUserTaskForm, self).__init__(form, **kargs)

        fields = [[str(i.id), "{0} ({1}: {2})".format(i.name, i.get_provider(), i.path)] for i in sources]
        fields.insert(0, ['', ''])
        self.source.choices = fields

        fields = [[str(i.id), i.name] for i in handlers]
        fields.insert(0, ['', ''])
        self.handler.choices = fields

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        source = Source.query.filter(Source.id == self.source.data, Source.user == current_user).first()
        if not source:
            self.source.errors.append('Invalid source!')
            return False

        handler = Handler.query.filter(Handler.id == self.handler.data, Source.user == current_user).first()
        if not handler:
            self.handler.errors.append('Invalid handler!')
            return False

        self.user_source = source
        self.user_handler = handler
        return True
