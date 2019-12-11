#!/usr/bin/env python
# coding=utf-8
# Stan 2018-07-09

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys

from werkzeug.wsgi import DispatcherMiddleware

from ..app import app


py_version = sys.version_info[:2]
PY2 = py_version[0] == 2


def encode(obj):
    return str(obj).encode('utf-8')


if app.config["APPLICATION_ROOT"] != '/':
    def simple2(env, resp):
        resp(b'200 OK', [(b'Content-Type', b'text/plain')])

        if app.debug:
            return [bytes("{0}: {1}\n".format(k, v)) for k, v in env.items()]

        return [b'Hello WSGI World\n']

    def simple3(env, resp):
        resp('200 OK', [('Content-Type', 'text/plain')])

        if app.debug:
            return [bytes("{0}: {1}\n".format(k, encode(v)), 'ascii') for k, v in env.items()]

        return ['Hello WSGI World\n']

    simple = simple2 if PY2 else simple3

    app.wsgi_app = DispatcherMiddleware(simple, {
        app.config["APPLICATION_ROOT"]: app.wsgi_app,
    })
