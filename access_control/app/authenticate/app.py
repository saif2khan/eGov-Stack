# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, render_template, redirect, url_for, jsonify, request, g

from authenticate import commands, public
from authenticate.extensions import bcrypt, db, login_manager, migrate, api, mail
from authenticate.settings import ProdConfig
import logging
from time import strftime
from logging.handlers import RotatingFileHandler

from authenticate.api import AuthApi, PublicAuthApi, UserApi, ScopesApi, CategoryApi, UserScopeMappingApi, \
                            ApplicationApi, AppContextApi


def create_app(config_object=ProdConfig):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """

    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)

    handler = RotatingFileHandler('authenticate.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    @app.after_request
    def after_request(response):
        """ Logging after every request. """
        # This avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if response.status_code != 500 and config_object.DEBUG == False:
            ts = strftime('[%Y-%b-%d %H:%M]')
            app.logger.info('%s %s %s %s %s %s %s',
                        ts,
                        request.remote_addr,
                        request.method,
                        request.scheme,
                        request.full_path,
                        request.form,
                        response.status)
        return response

    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    api.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        if error_code == 401:
            return jsonify({
                'error': 'Not authenticated'
            }), error_code
        return jsonify({
            'error': '{0}'.format(error_code)
        }), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
        }

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.initial_setup)
