#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-13

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os

from .. import app


def get_user_templates(user):
    home = os.path.join(app.root_path, 'templates', 'custom')

    try:
        ldir = os.listdir(home)
    except OSError:
        pass
    else:
        for name in ldir:
            tpname, ext = os.path.splitext(name)
            if ext == '.html':
                yield tpname

    home = os.path.join(app.root_path, 'templates', 'custom', user.username)

    try:
        ldir = os.listdir(home)
    except OSError:
        pass
    else:
        for name in ldir:
            tpname, ext = os.path.splitext(name)
            if ext == '.html':
                yield "{0}/{1}".format(user.username, tpname)
