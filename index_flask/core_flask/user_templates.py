#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-13

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import current_app


def get_user_templates(user):
    with current_app.app_context():
        for i in ('', user.username):
            home = os.path.join(current_app.root_path, 'templates', 'custom')

            try:
                ldir = os.listdir(home)
            except OSError:
                pass
            else:
                for name in ldir:
                    template_name, ext = os.path.splitext(name)
                    if ext == '.html':
                        yield "{0}/{1}".format(i, template_name) if i else \
                              template_name
