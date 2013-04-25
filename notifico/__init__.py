# -*- coding: utf8 -*-
from functools import wraps

from redis import Redis
from flask import (
    Flask,
    g,
    redirect,
    url_for
)
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from notifico.util import pretty

db = SQLAlchemy()
sentry = Sentry()
cache = Cache()


def user_required(f):
    """
    A decorator for views which required a logged in user.
    """
    @wraps(f)
    def _wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('account.login'))
        return f(*args, **kwargs)
    return _wrapped


def group_required(name):
    """
    A decorator for views which required a user to be member
    to a particular group.
    """
    def _wrap(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            if g.user is None or not g.user.in_group(name):
                return redirect(url_for('account.login'))
            return f(*args, **kwargs)
        return _wrapped
    return _wrap


def create_instance():
    """
    Construct a new Flask instance and return it.
    """
    app = Flask(__name__)
    app.config.from_object('notifico.default_config')

    # Check to see if we should handle routing for static assets
    # ourself (handy for small and quick deployments). A large
    # deploy should be handling static assets through a forward
    # cache or nginx/lighttpd/apache/etc...
    if app.config.get('HANDLE_STATIC'):
        import os.path
        from werkzeug import SharedDataMiddleware

        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/': os.path.join(os.path.dirname(__file__), 'static')
        })

    # If we're running in production we want to ensure errors
    # get logged.
    if not app.debug:
        # If sentry (http://getsentry.com) is configured for
        # error collection we should use it.
        if app.config.get('SENTRY_DSN'):
            sentry.dsn = app.config.get('SENTRY_DSN')
            sentry.init_app(app)

    # Setup our redis connection (which is already thread safe)
    app.redis = Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )
    cache.init_app(app, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': app.redis,
        'CACHE_OPTIONS': {
            'key_prefix': 'cache_'
        }
    })
    db.init_app(app)

    # Initialize all our blueprints
    from notifico.views.account import account
    from notifico.views.public import public

    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(public)

    # cia.vc XML-RPC kludge.
    from notifico.services.hooks.cia import handler
    handler.connect(app, '/RPC2')

    # Setup some custom Jinja2 filters.
    app.jinja_env.filters['pretty_date'] = pretty.pretty_date
    app.jinja_env.filters['plural'] = pretty.plural

    from notifico.services import stats
    app.jinja_env.globals['g_total_messages'] = stats.total_messages
    app.jinja_env.globals['g_total_users'] = stats.total_users
    app.jinja_env.globals['g_total_projects'] = stats.total_projects

    return app
