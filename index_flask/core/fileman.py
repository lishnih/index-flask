#!/usr/bin/env python
# coding=utf-8
# Stan 2016-05-22

from __future__ import ( division, absolute_import,
                         print_function, unicode_literals )

import os, logging


def list_files(path, root, override_url=None):
    if root:
        fullpath = "{0}{1}".format(root, path)

    if override_url:
        path = override_url

    dirlist = []
    filelist = []

    try:
        ldir = os.listdir(fullpath)

    except OSError as e:
        logging.warning("OSError '{0}'".format(e.message))

    else:
        for name in ldir:
            fullname = os.path.join(fullpath, name)
            url = '{0}{1}'.format(path, name)
            if os.path.isdir(fullname):
                dirlist.append([name, url])
            else:
                filelist.append([name, url])

    return dirlist, filelist
