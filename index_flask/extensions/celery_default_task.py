#!/usr/bin/env python
# coding=utf-8
# Stan 2018-12-21

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import random
import time
from importlib import import_module

from ..app import app, celery


@celery.task(bind=True)
def run_task_async(self, handler_dict, options):
#   message = 'File {0} in progress...'.format(i)
#   self.update_state(state='PROGRESS', meta={
#       'current': i,
#       'total': total,
#       'status': message,
#   })

    name = handler_dict.get('name')
    rev = handler_dict.get('rev')
    module = handler_dict.get('module')
    entry = handler_dict.get('entry')
    key = handler_dict.get('key')

    error = ''
    while True:
        # Load module
        try:
            mod = import_module(module)

        except Exception as e:
            error = "Error during loading: {0}".format(e)
            break

        # Load function, options and run
        func = getattr(mod, entry) if hasattr(mod, entry) else None
        if func:
            if task.handler.key:
                status = func(**{task.handler.key: options})

            else:
                status = func(options)

        else:
            app.logger.warning("Wrong entry: {0}".format(task.handler.entry))

        break

    return {
        'current': 100,
        'total': 100,
        'status': 'Task completed!',
        'result': "{0}".format('Completed'),
    }
