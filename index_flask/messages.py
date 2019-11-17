#!/usr/bin/env python
# coding=utf-8
# Stan 2019-11-15

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from . import config


SEND_VERIFICATION = """Welcome {{0}}!

Thank you for registering for an {INDEX_PORTAL_NAME} account.
To activate your account, simply click on the link below or paste this link into the URL field of your favorite browser:

{{1}}

If you have trouble confirming or accessing your account, please answer this email.

Best regards,
{INDEX_PORTAL_NAME} Team
""".format(INDEX_PORTAL_NAME = config.INDEX_PORTAL_NAME)
