#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-11

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, jsonify, flash
from jinja2 import Markup, escape

from flask_principal import Permission, RoleNeed

from ..core.backwardcompat import *

from ..app import safe_str


debug_permission = Permission(RoleNeed('debug'))


def swap(s, limit=60):
    if isinstance(s, basestring):
        s = escape(s)
        if len(s) > limit:
            s = Markup("""<span class="truncated">{0}</span>
<span class="quoted" title="{1}">[...]</span>""".format(s[0:limit-20], s))

    return s


def render_format(tmpl_name, flash_t=None, **kargs):
    format = request.values.get('format')

    if not debug_permission.can():
        kargs.pop('debug')

    if format == 'json':
        for key, val in kargs.items():
            if not isinstance(val, all_types):
                kargs.pop(key)

        if flash_t:
            message, result = flash_t if len(flash_t) > 1 else flash_t, 'prompt'
            kargs['flash_cat'] = result
            kargs['flash_message'] = message

        if 'rows' in kargs:
            kargs['rows'] = [[safe_str(None, i) for i in row] for row in kargs['rows']]
            kargs['rows'] = [[swap(i) for i in row] for row in kargs['rows']]

        return jsonify(**kargs)

    else:
        if flash_t:
            flash(*flash_t)

        if 'rows' in kargs:
            kargs['rows'] = [[swap(i) for i in row] for row in kargs['rows']]

        return render_template(tmpl_name, **kargs)
