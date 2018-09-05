# -*- coding: utf-8 -*-
from flask_restful import Resource, inputs, reqparse
from flask import Flask, jsonify, request, g
from authenticate.utils import abort
from authenticate.extensions import api, db, auth
from authenticate.settings import Config
from authenticate.api.user.models import User
from authenticate.api.app_contexts.models import AppContext
import datetime as dt

parser = reqparse.RequestParser(bundle_errors=True)


class AppContextApi(Resource):
    @auth.login_required
    def get(self, app_context_id=None):
        if not g.user.is_root_admin:
            return abort(401)
        if not app_context_id:
            app_contexts = AppContext.query.all()
            return {
                'app_contexts': [app_context.serialized for app_context in app_contexts],
                'is_successful': True
            }

        app_context = AppContext.query.filter_by(id=app_context_id).first()

        if not app_context:
            abort(401)

        return app_context.serialized

    @auth.login_required
    def post(self, app_context_id=None):
        data = request.values

        if not g.user.is_root_admin:
            return abort(401)

        if data.get('id', app_context_id):
            app_context_check = AppContext.query.filter(
                (AppContext.name == data.get('name', None)) &
                (AppContext.id != data.get('id', app_context_id))
            ).first()
            if app_context_check:
                return {
                    'message': 'AppContext name already in use under app_context ID {}' \
                        .format(app_context_check.id),
                    'is_successful': False
                }
            app_context = AppContext.query.filter_by(id=data.get('id', app_context_id)).first()
            if not app_context:
                return {
                    'message': 'App context does not exist',
                    'is_successful': False
                }
            app_context.name = data.get('name', app_context.name)
            if data.get('context_credentials', None):
                try:
                    app_context.context_credentials = data.get('context_credentials',
                        app_context.context_credentials)
                except:
                    return {
                        'message': 'Context credentials must be in JSON format',
                        'is_successful': False
                    }
            app_context.application_id = data.get('application_id', app_context.application_id)
            db.session.commit()
            return {
                'message': 'AppContext updated successfully.',
                'is_successful': True
            }

        app_context_check = AppContext.query.filter_by(name=data.get('name', None)).first()
        if app_context_check:
            return {
                'message': 'AppContext name already in use under app_context ID {}'
                    .format(app_context_check.id),
                'is_successful': False
            }
        app_context = AppContext()
        if not data.get('name', None):
            return {
                'message': 'Context name missing',
                'is_successful': False
            }
        app_context.name = data.get('name', None)
        try:
            app_context.context_credentials = data.get('context_credentials', None)
        except:
            return {
                'message': 'Context credentials must be in JSON format',
                'is_successful': False
            }
        if not data.get('application_id', None):
            return {
                'message': 'Application ID missing',
                'is_successful': False
            }
        app_context.application_id = data.get('application_id', None)
        db.session.add(app_context)
        db.session.commit()

        return {
            'message': 'AppContext added successfully.',
            'app_context_id': app_context.id,
            'is_successful': True
        }

    @auth.login_required
    def delete(self, app_context_id=None):
        if not g.user.is_root_admin:
            return abort(401)
        app_context = AppContext.query.filter_by(id=app_context_id).first()
        if not app_context:
            return {
                'message': 'App context does not exist',
                'is_successful': False
            }
        app_context.delete()
        return {
            'message': 'AppContext deleted successfully.',
            'is_successful': True
        }

api.add_resource(AppContextApi,
                 '/appContexts',
                 '/appContexts/<int:app_context_id>')
