#!/usr/bin/env python
# coding=utf-8
# Stan 2019-07-06

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask_login import login_required, current_user

from ..app import app
from ..core_flask.render_response import render_ext


# ===== Functions =====

def get_key(option):
    try:
        if option.type == 'int':
            return int(option.value)

        elif option.type == 'bool':
            return True if option.value == 'true' else False

        else:
            return option.value

    except:
        return ''


# ===== Routes =====

@app.route("/user_options", methods=['GET', 'POST'])
def user_options():
    options = {i.name: get_key(i) for i in current_user.options}
    return render_ext(
        format = 'json',
        name = '' if current_user.is_anonymous else current_user.name,
        options = options,
    )
