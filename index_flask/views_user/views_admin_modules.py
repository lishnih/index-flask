#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-28

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import request, jsonify, redirect, flash
from jinja2 import Markup, escape

from flask_login import login_required
from flask_principal import Permission, RoleNeed

from ..app import app, db
from ..core.functions import get_next
from ..core.html_helpers import parse_input, parse_span, highlighted
from ..core.load_modules import is_loaded
from ..core.render_response import render_ext
from ..models.module import Module


# ===== Roles =====

admin_permission = Permission(RoleNeed('admin'))


# ===== Routes =====

@app.route('/admin/modules', methods=['GET', 'POST'])
@login_required
@admin_permission.require(403)
def admin_modules():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete_record':
            id = request.form.get('id')
            if id:
                module = Module.query.filter_by(id=id).first()
                if module:
                    db.session.delete(module)

        elif action == 'toggle_record':
            id = request.form.get('id')
            checked = request.form.get('checked')
            checked = True if checked == 'true' else False
            if id:
                module = Module.query.filter_by(id=id).first()
                if module:
                    if checked:
                        if module.active:
                            return jsonify(result='rejected', message='The module is already active.')

                    else:
                        if not module.active:
                            return jsonify(result='rejected', message='The module is already disabled.')

                    module.active = checked

        if action:
            db.session.commit()

        return jsonify(result='accepted', message=action)

    s = Module.query
    total = s.count()

    modules = s.order_by('folder', 'name').all()
    names = [i.name for i in Module.__table__.c]
    rows = []
    for module in modules:
        row = []
        for i in names:
            if i == 'active':
                row.append(parse_input('', module.active, 'toggle_record',
                    id = module.id,
                ))
            else:
                row.append(escape(module.__dict__.get(i)))

        # Delete
        row.append(parse_span('', '[ x ]', 'delete_record',
            id = module.id,
        ))
        # On the disk
        fl = os.path.isfile(os.path.join(app.root_path, module.folder, "{0}.py".format(module.name)))
        row.append(highlighted('Yes', 'success') if fl else highlighted('No', 'danger'))
        # Is loaded
        fl = is_loaded(module.name, module.folder)
        row.append(highlighted('Yes', 'success') if fl else highlighted('No', 'danger'))

        rows.append(row)

    names.append('Delete')
    names.append('On the disk')
    names.append('Is loaded')

    return render_ext('admin/table_unsafe.html',
             title = 'App modules',
             names = names,
             rows = rows,
             total = total,
           )
