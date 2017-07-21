#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import logging

from index_flask.app import app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    app.run(debug=True)
