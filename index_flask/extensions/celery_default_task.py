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
    app.logger.debug("Starting...")
    app.logger.info(handler_dict)
    app.logger.info(options)
#   message = 'File {0} in progress...'.format(i)
#   self.update_state(state='PROGRESS', meta={
#       'current': i,
#       'total': total,
#       'status': message,
#   })

#   name = handler_dict.get('name')
#   rev = handler_dict.get('rev')
    module = handler_dict.get('module')
    entry = handler_dict.get('entry')
    key = handler_dict.get('key')

    error = exception = ''
    while True:
        # Load module
        try:
            mod = import_module(module)

        except Exception as e:
            exception = "Error during loading: {0}".format(e)
            break

        # Load function
        if hasattr(mod, entry):
            func = getattr(mod, entry)

        else:
            error = "Wrong entry: {0}".format(entry)
            break

        # Run
        try:
            if key:
                status = func(**{key: options})

            else:
                status = func(options)

        except Exception as e:
            exception = "Error during running: {0}".format(e)
            break

        break

    if error:
        app.logger.error(error)

    elif exception:
        app.logger.exception(exception)

    return {
        'current': 100,
        'total': 100,
        'status': 'Task completed!',
        'result': "{0} (Error: {1} / Exception {2})".format('Completed', error, exception),
    }
