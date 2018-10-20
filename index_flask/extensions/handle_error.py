#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-27

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import request, jsonify
from werkzeug.exceptions import HTTPException

from ..app import app


if app.debug:
    @app.errorhandler(404)
    def page_not_found(e):
        code = 404

        app.logger.exception("Not Found ({0}): ({1})".format(code, str(e)))

        return jsonify(error=str(e),
            url=request.url, root=request.url_root), code

else:
    @app.errorhandler(Exception)
    def handle_error(e):
        code = e.code if isinstance(e, HTTPException) else 500

        app.logger.exception("HTTP Exception ({0}): ({1})".format(code, str(e)))

        return jsonify(error=str(e)), code
