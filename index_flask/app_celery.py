#!/usr/bin/env python
# coding=utf-8
# Stan 2016-06-07

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from .app import celery

from .extensions.celery_send_email_task import send_email_async
from .extensions.celery_send_csv_task import send_csv_async
from .extensions.celery_default_task import run_task_async
