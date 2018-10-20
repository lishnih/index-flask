#!/usr/bin/env python
# coding=utf-8
# Stan 2018-08-03

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from ..app import app


@app.context_processor
def inject_app_debug():
    return dict(app_debug = app.debug)
