#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-19

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import multiprocessing
import json
from datetime import datetime
from importlib import import_module

from sqlalchemy.sql import select, column, table, and_

from ..main import app, db
from ..models.handler import Handler
from ..models.source import Source
from ..models.source_task import SourceTask


def get_cloud(user, provider_name):
    usersocialauth = table('social_auth_usersocialauth')
    user_id = column('user_id')
    provider = column('provider')
    s = select(['*'], and_(user_id == user.id, provider == provider_name), usersocialauth)

    res = db.session.execute(s)

    return res.fetchone()


def worker(task_id):
    task = SourceTask.query.filter_by(id=task_id).first()
    if task:
        # Load module
        mod = import_module(task.handler.module)

        # Load function, options and run
        func = getattr(mod, task.handler.entry) \
               if hasattr(mod, task.handler.entry) else None

        if func:
            options = task.handler.options
#           for key, value in options.items():
#               res = re.split('^{{ (.+) }}', value, 1)
#               if len(res) == 3:
#                   _, code, value = res
#                   options[key] = decode(code, value)

            options['files'] = task.source.path_id
            options['source_id'] = task.source.id
            options['path'] = task.source.path
            options['provider'] = task.source.provider
            options['dbhome'] = task.source.user.home

            cloud = get_cloud(task.source.user, task.source.provider)
            parsed = json.loads(cloud.extra_data)
            options['access_token'] = parsed.get('access_token')

            for i in options:
                print(i, options[i])

            if task.handler.key:
                status = func(**{task.handler.key: options})

            else:
                status = func(options)

        else:
            app.logger.warning("Wrong entry: {0}".format(task.handler.entry))

        task.finished = datetime.utcnow()
        task.status = status or 1
        db.session.commit()

    else:
        app.logger.warning("Wrong task: {0}".format(task.name))


def source_task_create(user_source, handler, mode='manual'):
    if handler == 'initial_scan':
        handler = Handler.query.filter_by(name='initial_scan').first()
#       mode = 'auto'

    user_source_task = SourceTask(
        source = user_source,
        handler = handler,
        mode = mode,
    )

    db.session.add(user_source_task)
    db.session.commit()

    if mode == 'auto':
        source_task_request(user_source_task)

    return user_source_task


def source_task_request(user_source_task):
#     if user_source_task.status:
#         print("Task in progress or finished:", user_source_task)
#         return

    user_source_task.status = -1
    db.session.commit()

    t = multiprocessing.Process(target=worker, args=(user_source_task.id,))
    t.start()
