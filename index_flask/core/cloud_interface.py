#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-16

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import os
import json
import logging

try:
    import dropbox
    from dropbox.files import FolderMetadata, FileMetadata
except ImportError as e:
    logging.error(e)
    dropbox = None

try:
    import yadisk
except ImportError as e:
    logging.error(e)
    yadisk = None


def get_cloud_files(cloud, dir_):
    # Empty 'dir_' means root dir

    dirs = []
    files = []

    parsed = json.loads(cloud.extra_data)

    if cloud.provider == 'dropbox-oauth2':
        token = parsed.get('access_token')
        if dropbox and token:
            dbx = dropbox.Dropbox(token)
            response = dbx.files_list_folder(dir_)
            dir_list, file_list = get_files_dropbox(response)
            dirs += dir_list
            files += file_list

            while response.has_more:
                response = dbx.files_list_folder_continue(response.cursor)
                dir_list, file_list = get_files_dropbox(response)
                dirs += dir_list
                files += file_list

        else:
            logging.error("Dropbox not loaded or token missed!")

    elif cloud.provider == 'google-oauth2':
        pass

    elif cloud.provider == 'mailru-oauth2':
        pass

    elif cloud.provider == 'yandex-oauth2':
        token = parsed.get('access_token')
        if yadisk and token:
            ya = yadisk.YaDisk(token=token)
            if not ya.check_token():
                pass

            if not dir_:
                dir_ = "/"      # "disk:/" | "app:/"
            response = ya.listdir(dir_)
            dir_list, file_list = get_files_yandex(response)
            dirs += dir_list
            files += file_list

        else:
            logging.error("Yandex Disk not loaded or token missed!")

    else:
        raise Exception("Provider unknown: {0}".format(cloud.provider))

    return dirs, files


def get_files_dropbox(response):
    dirs = []
    files = []
    for i in response.entries:
        if isinstance(i, FolderMetadata):
            dirs.append({'name': i.name, 'path': i.path_display, 'path_id': i.id})
        elif isinstance(i, FileMetadata):
            files.append({'name': i.name, 'path': i.path_display, 'path_id': i.id})
        else:
            logging.debug(i)

    return dirs, files


def get_files_yandex(response):
    dirs = []
    files = []
    for i in response:
        if i.type == 'dir':
            dirs.append({'name': i.name, 'path': i.path, 'path_id': i.path})
        elif i.type == 'file':
            files.append({'name': i.name, 'path': i.path, 'path_id': i.path})
        else:
            logging.debug(i)

    return dirs, files
