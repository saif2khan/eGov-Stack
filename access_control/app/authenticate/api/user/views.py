# -*- coding: utf-8 -*-
from flask_restful import Resource, inputs, reqparse
from flask import Flask, jsonify, request, url_for, g
from authenticate.extensions import api, db, auth
from authenticate.settings import Config
from authenticate.utils import try_parsing_date, send_email, validate_email, abort
from authenticate.api.user.models import User
from authenticate.api import PublicAuthApi
from itsdangerous import URLSafeTimedSerializer as Serializer
import datetime as dt
import phonenumbers

parser = reqparse.RequestParser(bundle_errors=True)


class UserApi(Resource):
    @auth.login_required
    def get(self, user_id=None):
        parser.add_argument('returnIdOnly', location='args')
        args = parser.parse_args()
        # list users
        if not user_id:
            users = User.query.filter_by(is_deleted=False).all()
            if args.get('returnIdOnly', None) == 'true':
                return {
                    'users': [user.id for user in 
                                list(filter(lambda d: g.user.can.view.user_id(d.id), users))],
                    'is_successful': True
                }
            return {
                'users': [user.serialized for user in 
                                list(filter(lambda d: g.user.can.view.user_id(d.id), users))],
                'is_successful': True
            }

        user = User.query.filter_by(id=user_id).first()

        if g.user.can.view.user_id(user.id):
            return user.serialized  
        else: 
            return abort(401)

    @auth.login_required
    def post(self, user_id=None):

        data = request.values

        if data.get('id', user_id):
            # mobile number is not required so only validate it if it was sent in the request
            if data.get('mobile_number', None):
                try:
                    int(data.get('mobile_number', None))
                except:
                    return {
                        'message': 'Invalid phone number',
                        'is_successful': False
                    }
                try:
                    phone_number = phonenumbers.parse(data.get('mobile_number', None), 
                                                                        Config.DEFAULT_PHONE_REGION)
                    phone_number = phonenumbers.format_number(phone_number, 
                                                                phonenumbers.PhoneNumberFormat.E164)
                except Exception as e:
                    return {
                        'message': str(e),
                        'is_successful': False
                    }
            if data.get('email', None):
                try:
                    validate_email(data.get('email', None))
                except Exception as e:
                    return {
                        'message': 'Email address not valid',
                        'is_successful': False
                    }
            if not hasattr(g, 'user') or not g.user or not g.user.can.modify.user_id(data.get('id', user_id)):
                return abort(401)
            user_name_check = User.query.filter(
                (User.username == data.get('username', None)) &
                (User.id != data.get('id', user_id))
            ).first()
            email_check = User.query.filter(
                (User.email == data.get('email', None)) &
                (User.id != data.get('id', user_id))
            ).first()
            if user_name_check:
                return {
                    'message': 'Username already in use',
                    'is_successful': False
                }
            if email_check:
                return {
                    'message': 'Email already in use',
                    'is_successful': False
                }
            user = User.query.filter_by(id=data.get('id', user_id)).first()
            if not user:
                return {
                    'message': 'User not found',
                    'is_successful': False
                }
            user.first_name = data.get('first_name', user.first_name)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.mobile_number = data.get('mobile_number', user.mobile_number)
            user.last_name = data.get('last_name', user.last_name)
            if data.get('password', None):
                user.set_password(data.get('password'))
            db.session.commit()

            return {
                'message': 'User updated successfully.',
                'is_successful': True
            }

        user_name_check = User.query.filter_by(username=data.get('username', None)).first()
        email_check = User.query.filter_by(email=data.get('email', None)).first()
        if user_name_check:
            return {         
                'message': 'Username already in use',
                'is_successful': False
            }
        if email_check:
            return {           
                'message': 'Email already in use',
                'is_successful': False
            }

        if data.get('mobile_number') and data.get('username') and \
            data.get('email') and data.get('first_name') and \
            data.get('last_name') and data.get('password'):
            pass
        else:
            return {           
                'message': 'All fields are required',
                'is_successful': False
            }
        if data.get('mobile_number', None):
            try:
                int(data.get('mobile_number', None))
            except:
                return {
                    'message': 'Invalid phone number',
                    'is_successful': False
                }
            try:
                phone_number = phonenumbers.parse(data.get('mobile_number', None), 
                                                            Config.DEFAULT_PHONE_REGION)
                phone_number = phonenumbers.format_number(phone_number, 
                                                          phonenumbers.PhoneNumberFormat.E164)
            except Exception as e:
                return {
                    'message': str(e),
                    'is_successful': False
                }
        else:
            phone_number = None
        if not validate_email(data.get('email', None)):
            return {
                'message': 'Email address not valid',
                'is_successful': False
            }
        user = User().create(first_name=data.get('first_name', None),
                             username=data.get('username', None),
                             mobile_number=phone_number,
                             email=data.get('email', None),
                             last_name=data.get('last_name', None))

        if data.get('password', None):
            user.set_password(data.get('password', None))

        db.session.commit()

        # Generate email verification token
        token = user.generate_auth_token()
        email_body = 'Please use the following token to verify your email: {}' \
            .format(api.url_for(PublicAuthApi, action='verify-email', 
                                        token=token, _external=True))
        send_email('admin@samagra.com', 'Please Verify Your Email', user.email, email_body)

        return {     
            'message': 'User added successfully.',
            'user_id': user.id,
            'is_successful': True
        }

    @auth.login_required
    def delete(self, user_id):
        if not g.user.can.delete.user_id(user_id):
            return abort(401)
        user = User.query.filter_by(id=user_id).first()
        if user and not user.is_deleted:
            user.roles = []
            user.is_deleted = True
            db.session.commit()
            return {
                'message': 'User deleted successfully.',
                'is_successful': True
            }
        else:
            return {
                'message': 'User id: {} is not found'.format(user_id)
            }


api.add_resource(UserApi,
                 '/users',
                 '/user/<int:user_id>')
