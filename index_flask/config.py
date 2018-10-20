#!/usr/bin/env python
# coding=utf-8

import os

here = os.path.abspath(os.path.dirname(__file__))
home = os.path.expanduser("~")

APPLICATION_ROOT = '/index'

INDEX_USERS_ROOT = '~/.config/index'
INDEX_SQLITE_HOME = os.path.join(home, '.config/index')

CSRF_ENABLED = True
SECRET_KEY = 'your-secret-key_\xfb+\x14-\xdf_\xbb=\x8f'

# SQL Alchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(os.path.join(here, 'app.db'))
SQLALCHEMY_MIGRATE_REPO = os.path.join(here, 'db_repository')
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_BINDS = {
  'logging': 'sqlite:///{0}'.format(os.path.join(INDEX_SQLITE_HOME, 'logging.db')),
  'indexing': 'sqlite:///{0}'.format(os.path.join(INDEX_SQLITE_HOME, 'indexing.db')),
  'http_requests': 'sqlite:///{0}'.format(os.path.join(INDEX_SQLITE_HOME, 'http_requests.db')),
}


# ===================
# === social_auth ===
# ===================

SOCIAL_AUTH_LOGIN_URL = '/index/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/index/accounts'
SOCIAL_AUTH_USER_MODEL = 'index_flask.models.user.User' # !!! index_flask
SOCIAL_AUTH_STORAGE = 'social_flask_sqlalchemy.models.FlaskStorage'
SOCIAL_AUTH_AUTHENTICATION_BACKENDS = (
    'social_core.backends.dropbox.DropboxOAuth2V2',
    'social_core.backends.google.GoogleOAuth2',
#   'social_core.backends.mailru.MailruOAuth2',
    'social_core.backends.yandex.YandexOAuth2',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'index_flask.common.pipeline.require_email',    # !!! index_flask
    'social_core.pipeline.mail.mail_validation',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.debug.debug',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.debug.debug',

    # the middleware implemented
#     'index_flask.common.pipeline.AuthAlreadyAssociatedMiddleware',
)
