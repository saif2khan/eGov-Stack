# -*- coding: utf-8 -*-
from flask_restful import Resource, inputs, reqparse
from flask import Flask, jsonify, request, g, url_for
from authenticate.utils import abort
from authenticate.extensions import api, auth, db
from authenticate.settings import Config
from authenticate.utils import send_email
from authenticate.api.user.models import User
from .models import InvalidToken
from itsdangerous import URLSafeTimedSerializer as Serializer
import datetime as dt

parser = reqparse.RequestParser(bundle_errors=True)


class AuthApi(Resource):
    @auth.login_required
    def get(self, action=None):
        if action == 'token':
            token = g.user.generate_auth_token()
            return {
                'token': token
            }
        if action == 'logout':
            if g.token != g.user.username:
                invalid_token = InvalidToken()
                invalid_token.token = g.token
                db.session.add(invalid_token)
                db.session.commit()
            return {
                'message': 'You have been logged out',
                'is_successful': True
            }
    def post(self, action=None):
        pass


class PublicAuthApi(Resource):
    def get(self, action=None):
        parser.add_argument('email', location='args')
        parser.add_argument('token', location='args')
        args = parser.parse_args()

        # Verify email address with token
        if action == 'verify-email':
            s = Serializer(Config.SECRET_KEY)
            try:
                email = s.loads(args.get('token'), salt="recover-key", max_age=3600)
                user = User.query.filter_by(email=email).first()
                if user:
                    user.email_verified = True
                    user.save()
                    return {
                        'message': 'Email verified',
                        'is_successful': True
                    }
            except Exception as e:
                return {
                    'message': 'Not Found',
                    'is_successful': False
                }

        # sends the password reset email to start the reset process
        """If a user has forgotten their password, they will be unable to login to retrieve it. 
        Therefore this route must be publicly accessible. Authentication is performed with the 
        secure token."""
        if action == 'reset-password':
            user = User.query.filter_by(email=args.get('email', None)).first()
            if user is None:
                return {
                    'message': 'Password reset initiated',
                    'is_successful': True
                }
            else:
                token = user.generate_auth_token()
                email_body = 'Please use the following token to reset your password: {}' \
                    .format(url_for('public.forgot_password', token=token, _external=True))
                send_email('admin@samagra.com', 'Password Reset', user.email, email_body)
                return {
                    'message': 'Password reset initiated',
                    'is_successful': True
                }
        return '', 204

    def post(self, action=None):
        parser.add_argument('token', location='args')
        args = parser.parse_args()
        data = request.values
        s = Serializer(Config.SECRET_KEY)
        try:
            email = s.loads(args.get('token'), salt="recover-key", max_age=3600)
        except:
            return {
                'message': 'Invalid token',
                'is_successful': False
            }
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(data.get('password', None))
            user.save()
            return {
                'message': 'User updated successfully',
                'is_successful': True
            }
        else:
            return {
                'message': 'No user found',
                'is_successful': False
            }


api.add_resource(AuthApi,
                 '/auth',
                 '/auth/<action>')

api.add_resource(PublicAuthApi,
                 '/public-auth',
                 '/public-auth/<action>')
