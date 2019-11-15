#!/usr/bin/env python
# coding=utf-8

import os
import platform


# Index configuration
INDEX_CONFIG_ID = 'index_flask'
INDEX_CONFIG_DIR = os.path.join('~', '.index', INDEX_CONFIG_ID)
INDEX_USERS_DIR = os.path.join(INDEX_CONFIG_DIR, 'users')
INDEX_SQLITE_HOME = os.path.join(INDEX_USERS_DIR, 'id1')
INDEX_CONFIG = '../credentials_cfg.py'

INDEX_REPORT_MAIL = 'lishnih@yandex.ru'
INDEX_REPORT_ID = platform.uname()[1]


# Flask configuration
APPLICATION_ROOT = '/index'
CSRF_ENABLED = True
SECRET_KEY = 'index_\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


# SQL Alchemy configuration
_dir = os.path.expanduser(INDEX_CONFIG_DIR)
SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(os.path.join(_dir, 'app.db'))
SQLALCHEMY_MIGRATE_REPO = os.path.join(_dir, 'db_repository')
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

_dir = os.path.expanduser(INDEX_SQLITE_HOME)
SQLALCHEMY_BINDS = {
  'logging': 'sqlite:///{0}'.format(os.path.join(_dir, '_logging.sqlite')),
  'indexing': 'sqlite:///{0}'.format(os.path.join(_dir, '_indexing.sqlite')),
  'http_requests': 'sqlite:///{0}'.format(os.path.join(_dir, '_http_requests.sqlite')),
}


# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


# Flask-Mail configuration
MAIL_SERVER = 'smtp.yandex.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = 'support@index.net.ru'


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
    'social_core.backends.yandex.YandexOAuth2',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'index_flask.common.pipeline.require_email',        # !!! index_flask
    'social_core.pipeline.mail.mail_validation',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.debug.debug',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.debug.debug',

    # the middleware implemented
#   'index_flask.common.pipeline.AuthAlreadyAssociatedMiddleware',
)


# https://python-social-auth.readthedocs.io/en/latest/backends/dropbox.html
SOCIAL_AUTH_DROPBOX_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_DROPBOX_OAUTH2_KEY')
SOCIAL_AUTH_DROPBOX_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_DROPBOX_OAUTH2_SECRET')


# https://python-social-auth.readthedocs.io/en/latest/backends/google.html
# https://developers.google.com/identity/protocols/googlescopes
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/drive.readonly',
#   'https://www.googleapis.com/auth/userinfo.profile',
#   'https://www.googleapis.com/auth/plus.me',
#   'https://www.googleapis.com/auth/userinfo.email',
]


# Yandex
SOCIAL_AUTH_YANDEX_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_YANDEX_OAUTH2_KEY')
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_YANDEX_OAUTH2_SECRET')
