# -*- coding: utf-8 -*-
from flask_restful import Resource, inputs, reqparse
from flask import Flask, jsonify, request, g
from authenticate.utils import abort
from authenticate.extensions import api, db, auth
from authenticate.settings import Config
from authenticate.api.user.models import User
from authenticate.api.applications.models import Application
import datetime as dt

parser = reqparse.RequestParser(bundle_errors=True)


class ApplicationApi(Resource):
    @auth.login_required
    def get(self, application_id=None):
        if not g.user.is_root_admin:
            return abort(401)
        if not application_id:
            applications = Application.query.all()
            return {
                'applications': [application.serialized for application in applications],
                'is_successful': True
            }

        application = Application.query.filter_by(id=application_id).first()

        return application.serialized

    @auth.login_required
    def post(self, application_id=None):
        data = request.values

        if not g.user.is_root_admin:
            return abort(401)

        if data.get('id', application_id):
            application_check = Application.query.filter(
                (Application.name == data.get('name', None)) &
                (Application.id != data.get('id', application_id))
            ).first()
            if application_check:
                return {
                    'message': 'Application name already in use under application ID {}' \
                        .format(application_check.id),
                    'is_successful': False
                }
            application = Application.query.filter_by(id=data.get('id', application_id)).first()
            if not application:
                return {
                    'message': 'Application does not exist',
                    'is_successful': False
                }
            application.name = data.get('name', application.name)
            if data.get('white_listed_ips', None):
                try:
                    application.white_listed_ips = data.get('white_listed_ips', 
                        application.white_listed_ips)
                except:
                    return {
                        'message': 'White listed IP\'s must be in JSON format',
                        'is_successful': False
                    }
            db.session.commit()
            return {
                'message': 'Application updated successfully.',
                'is_successful': True
            }

        application_check = Application.query.filter_by(name=data.get('name', None)).first()
        if application_check:
            return {
                'message': 'Application name already in use under application ID {}' \
                    .format(application_check.id),
                'is_successful': False
            }
        application = Application()
        if not data.get('name', None):
            return {
                'message': 'Application name missing',
                'is_successful': False
            }
        application.name = data.get('name', None)
        try:
            application.white_listed_ips = data.get('white_listed_ips', None)
        except:
            return {
                'message': 'White listed IP\'s must be in JSON format',
                'is_successful': False
            }

        db.session.add(application)
        db.session.commit()

        return {
            'message': 'Application added successfully.',
            'application_id': application.id,
            'is_successful': True
        }

    @auth.login_required
    def delete(self, application_id=None):
        if not g.user.is_root_admin:
            return abort(401)
        application = Application.query.filter_by(id=application_id).first()
        if not application:
            return {
                'message': 'Application does not exist',
                'is_successful': False
            }
        application.delete()
        return {
            'message': 'Application deleted successfully.',
            'is_successful': True
        }
            


api.add_resource(ApplicationApi,
                 '/applications',
                 '/applications/<int:application_id>')
