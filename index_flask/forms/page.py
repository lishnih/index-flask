#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_login import current_user

from wtforms import (Form, SubmitField, StringField, TextAreaField,
                     HiddenField, validators)

from ..models.page import Page


class EditForm(Form):
    name = StringField('Name', [validators.Required()])
    title = StringField('Title', [validators.Required()])
    content = TextAreaField('Content', [validators.Required()],
        render_kw={"rows": "10"}
    )
    uid = HiddenField()

    submit = SubmitField('Submit')

    def __init__(self, form, user_page, **kargs):
        super(EditForm, self).__init__(form, **kargs)

        if not form:
            self.name.data = user_page.name
            self.title.data = user_page.title
            self.content.data = user_page.content
            self.uid.data = user_page.uid

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        page = Page.query.filter_by(uid=self.uid.data).first()
        if page and page.user != current_user:
            self.name.errors.append('The page is not available!')
            return False

        self.page = page
        return True
