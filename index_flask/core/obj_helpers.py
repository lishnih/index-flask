#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-14

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import json

from flask import request, render_template, jsonify, flash

from ..core.backwardcompat import *


def get_query_string(**kargs):
    return json.dumps(kargs)


def get_query(request_form):
    if request_form:
        return json.loads(request_form)
