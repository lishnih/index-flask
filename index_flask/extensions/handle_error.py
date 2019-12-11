#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-27

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, jsonify
from werkzeug.exceptions import HTTPException

from ..app import app


@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning('Page not found')

    return jsonify(code=404, url=request.url), 404


if app.debug:
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(code=500, url=request.url), 500


else:
    @app.errorhandler(Exception)
    def handle_error(e):
        if isinstance(e, HTTPException):
            code = e.code
            app.logger.exception("HTTP Exception ({0}): ({1})".format(code, str(e)))

        else:
            code = 500
            app.logger.exception("Exception ({0}): ({1})".format(code, str(e)))

        return jsonify(code=code), code
