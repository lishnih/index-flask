#!/usr/bin/env python
# coding=utf-8
# Stan 2018-09-15

from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

from flask import g

from flask_login import current_user

from social_flask.utils import load_strategy
from social_flask.routes import social_auth
from social_flask.template_filters import backends
from social_flask_sqlalchemy.models import init_social
from social_core.exceptions import SocialAuthBaseException
from social_flask_sqlalchemy import models

from ..app import app, db
from ..common import filters
from ..common.utils import common_context, url_for as common_url_for


app.register_blueprint(social_auth)
init_social(app, db.session)

models.PSABase.metadata.create_all(db.engine)


@app.before_request
def global_user():
    # evaluate proxy value
    g.user = current_user


@app.teardown_appcontext
def commit_on_success(error=None):
    print(222, error)
    if error is None:
        db.session.commit()
    else:
        db.session.rollback()

    db.session.remove()


# Make current user available on templates
@app.context_processor
def inject_user():
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}


@app.context_processor
def load_common_context():
    return common_context(
        app.config['SOCIAL_AUTH_AUTHENTICATION_BACKENDS'],
        load_strategy(),
        getattr(g, 'user', None),
        app.config.get('SOCIAL_AUTH_GOOGLE_PLUS_KEY')
    )


app.context_processor(backends)
app.jinja_env.filters['backend_name'] = filters.backend_name
app.jinja_env.filters['backend_class'] = filters.backend_class
app.jinja_env.filters['icon_name'] = filters.icon_name
app.jinja_env.filters['social_backends'] = filters.social_backends
app.jinja_env.filters['legacy_backends'] = filters.legacy_backends
app.jinja_env.filters['oauth_backends'] = filters.oauth_backends
app.jinja_env.filters['filter_backends'] = filters.filter_backends
app.jinja_env.filters['slice_by'] = filters.slice_by
app.jinja_env.globals['url'] = common_url_for


@app.errorhandler(500)
def error_handler(error):
    if isinstance(error, SocialAuthBaseException):
        return redirect('/index/socialerror')


@app.route("/socialerror")
def socialerror():
    k
    return render_template('base.html',
        title = 'Index',
        text = 'Welcome!',
    )
