#!/usr/bin/env python
# coding=utf-8
# Stan 2019-07-12

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, url_for

from flask_login import current_user

from wtforms import Form, StringField, HiddenField, SubmitField, validators

from ..models.favorite import Favorite


class AddFavoriteForm(Form):
    name = StringField('Name:', [
            validators.DataRequired(),
        ],
        render_kw = {
            "placeholder": "Name (required)",
        }
    )
    url = StringField('Url:', [
            validators.DataRequired(),
        ],
        render_kw = {
            "placeholder": "URL (required)",
            "id": "url",
        }
    )
    submit = SubmitField('Append')

    def __init__(self, form, url=None, **kargs):
        super(AddFavoriteForm, self).__init__(form, **kargs)

        if not self.url.data:
            self.url.data = url or \
                            request.referrer or \
                            url_for('index', _external=True)

        if not self.name.data:
            self.name.data = next( (i for i in self.url.data.split('/')[::-1] if i), 'Name' ).title()

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        favorite, i = True, 0
        while favorite:
            name = "{0} [{1}]".format(self.name.data, i) if i else \
                   self.name.data
            favorite = Favorite.query.filter_by(_user_id=current_user.id, name=name).first()
            i += 1

        self.name.data = name

        return True
