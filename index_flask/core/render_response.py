#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-11

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, jsonify, flash

from ..core.backwardcompat import *


def render_template_custom(tmpl_name, **kargs):
    custom = request.args.get('custom')

    if not custom:
        flash("На этой странице Вы можете задать шаблон")
        custom_name = tmpl_name
    else:
        custom_name = 'custom/{0}.html'.format(custom)
    return render_template(custom_name, **kargs)


def render_format(tmpl_name, flash_t=None, **kargs):
    format = request.args.get('format')

    if format == 'json':
        for key, val in kargs.items():
            if not isinstance(val, all_types):
                kargs.pop(key)

        if flash_t:
            message, result = flash_t if len(flash_t) > 1 else flash_t, 'prompt'
            kargs['flash_cat'] = result
            kargs['flash_message'] = message

        return jsonify(**kargs)

    else:
        if flash_t:
            flash(*flash_t)
        return render_template(tmpl_name, **kargs)
