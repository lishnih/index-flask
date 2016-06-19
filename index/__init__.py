#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import Flask, request, g, jsonify

from flask_login import LoginManager

from sqlalchemy.orm import sessionmaker, scoped_session

from .ext.backwardcompat import *
from .ext.settings import Settings
from .ext.db import initDb

from . import config


app = Flask(__name__, static_url_path='')
app.config.from_object(config)
# app.config.from_pyfile('app.cfg')


def get_conn():
    if 'engine' not in g:
        s = Settings()
        g.db_uri = "{0}:///{1}/{2}".format('sqlite', s.system.path, 'xls0p3.sqlite')
        g.engine, g.metadata, g.relationships = initDb(g.db_uri)
    return g.engine.connect()


from . import (
  view_j2,      # j2 package
  views,        # Common views
  views_user,   # User views
  views_debug,  # Debug views
)


@app.route("/j2", methods=["GET", "POST"])
def j2():
    get_conn()
    session = scoped_session(sessionmaker(bind=g.engine))
    g.s = session()
    return jsonify(view_j2.view_j2(request))
