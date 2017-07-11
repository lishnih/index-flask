#!/usr/bin/env python
# coding=utf-8
# Stan 2017-07-11

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

from flask import request, render_template, flash


def render_template_custom(tmpl_name, **kargs):
    custom = request.args.get('custom')

    if not custom:
        flash("На этой странице Вы можете задать шаблон")
        custom_name = tmpl_name
    else:
        custom_name = 'custom/{0}.html'.format(custom)
    return render_template(custom_name, **kargs)
