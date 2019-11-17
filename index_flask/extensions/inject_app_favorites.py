#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from ..app import app, db
from ..models.favorite import Favorite


@app.context_processor
def inject_app_debug():
    res = Favorite.query.limit(20).all()

    return dict(app_favorites = [[row.name, row.url] for row in res])
