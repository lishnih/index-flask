#!/usr/bin/env python
# coding=utf-8
# Stan 2016-04-24

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os

from flask import render_template, send_from_directory, url_for, abort
from flask_principal import Permission, RoleNeed

from ..core.fileman import list_files

from ..app import app

# ===== Options =====

dir_name = 'test'
test_url = '/{0}/'.format(dir_name)


# ===== Roles =====

debug_permission = Permission(RoleNeed('debug'))


# ===== Routes =====

@app.route(test_url)
@app.route('{0}<path:path>'.format(test_url))
def test_dir(path=''):
    if not debug_permission.can():
        abort(404)

    abspath = os.path.join(app.root_path, dir_name, path)
    if not os.path.exists(abspath):
        return render_template('base.html',
                 content_head = 'Path not found!',
                 text = path,
               )

    if not path or path[-1] == '/':
        test_path_url = '/{0}/{1}'.format(dir_name, path)
        dirlist, filelist = list_files(test_path_url, app.root_path, url_for('test_dir', path=path))

        return render_template('views/filelist.html',
                 title = 'Testing directory',
                 path = test_path_url,
                 dirlist = dirlist,
                 filelist = filelist,
               )

    else:
        test_path_url = '{0}/{1}'.format(dir_name, path)
        return send_from_directory(app.root_path, test_path_url)
