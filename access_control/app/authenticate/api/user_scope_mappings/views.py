# -*- coding: utf-8 -*-
from flask_restful import Resource, inputs, reqparse
from flask import Flask, jsonify, request, g
from authenticate.utils import abort
from authenticate.extensions import api, db, auth
from authenticate.settings import Config
from authenticate.api.user.models import User
from authenticate.api.user_scope_mappings.models import UserScopeMapping
from authenticate.api.categories.models import Category
import datetime as dt

parser = reqparse.RequestParser(bundle_errors=True)


class UserScopeMappingApi(Resource):
    @auth.login_required
    def get(self, user_scope_mapping_id=None, scope_id=None, category_id=None, user_id=None):
        if scope_id:
            user_scope_mappings = UserScopeMapping.query.filter_by(scope_id=scope_id).all()
            user_scope_mappings_list = []
            for mapping in user_scope_mappings:
                for user in mapping.users:
                    if g.user.can.view.user_scope_mapping_id(mapping.id):
                        serialized = mapping.serialized
                        serialized['user_id'] = user.id
                        user_scope_mappings_list.append(serialized)
            if not user_scope_mappings:
                return {
                    'message': 'userScopeMapping not found',
                    'is_successful': False
                }
            return {
                'user_scope_mappings': user_scope_mappings_list,
                'is_successful': True
            }

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            user_scope_mappings = UserScopeMapping.query.join(User.user_scope_mappings) \
                                                                    .filter(User.id == user.id).all()
            if not user:
                return {
                    'message': 'User not found',
                    'is_successful': False
                }
            return {
                'user_scope_mappings': [user_scope_mapping.serialized for 
                    user_scope_mapping in list(filter(lambda d: g.user.can.view.user_scope_mapping_id(d.id), 
                    user_scope_mappings))],
                'is_successful': True
            }

        if category_id:
            categories = Category.query.filter_by(id=category_id).all()
            user_scope_mappings = []
            for category in categories:
                for scope in category.scopes:
                    for mappings in scope.user_scope_mappings:
                        user_scope_mappings.append(mappings)
            user_scope_mappings_list = []
            for mapping in user_scope_mappings:
                for user in mapping.users:
                    if g.user.can.view.user_scope_mapping_id(mapping.id):
                        serialized = mapping.serialized
                        serialized['user_id'] = user.id
                        user_scope_mappings_list.append(serialized)
            return {
                'user_scope_mappings': user_scope_mappings_list,
                'is_successful': True
            }   

        if not user_scope_mapping_id:
            user_scope_mappings = UserScopeMapping.query.all()
            user_scope_mappings_list = []
            for mapping in user_scope_mappings:
                for user in mapping.users:
                    if g.user.can.view.user_scope_mapping_id(mapping.id):
                        serialized = mapping.serialized
                        serialized['user_id'] = user.id
                        user_scope_mappings_list.append(serialized)
            return {
                'user_scope_mappings': user_scope_mappings_list,
                'is_successful': True
            }

        user_scope_mapping = UserScopeMapping.query.filter_by(id=user_scope_mapping_id).first()

        if g.user.can.view.user_scope_mapping_id(user_scope_mapping.id):
            user_scope_mappings_list = []
            for user in user_scope_mapping.users:
                if g.user.can.view.user_scope_mapping_id(user_scope_mapping.id):
                    serialized = user_scope_mapping.serialized
                    serialized['user_id'] = user.id
                    user_scope_mappings_list.append(serialized)
            return {
                'user_scope_mappings': user_scope_mappings_list,
                'is_successful': True
            } 
        else: 
            return abort(401)

    @auth.login_required
    def post(self, user_scope_mapping_id=None):
        data = request.values

        user = User.query.filter_by(id=data.get('user_id', None)).first()
        if not user:
            return {
                'message': 'Unable to add/modify user_scope_mapping for user id: {}. User not found' \
                    .format(data.get('user_id', None)),
                'is_successful': False
            }

        if data.get('user_scope_mapping_id', user_scope_mapping_id):
            if not g.user.can.modify.user_scope_mapping_id(data.get('user_scope_mapping_id', 
                                                                            user_scope_mapping_id)):
                return abort(401)
            user_scope_mapping = UserScopeMapping.query.filter(
                (UserScopeMapping.id == data.get('user_scope_mapping_id', user_scope_mapping_id)) &
                (UserScopeMapping.users.any(id=data.get('user_id', None)))
            ).first()
            if not user_scope_mapping:
                return {
                    'message': 'UserScopeMapping not found for user id: {}' \
                        .format(data.get('user_id', None)),
                    'is_successful': False
                }
            if not data.get('role', None) in Config.APPROVED_ROLES:
                return {
                    'message': 'Role must be in {}'.format(str(Config.APPROVED_ROLES)),
                    'is_successful': False
                }
            user_scope_mapping.role = data.get('role', user_scope_mapping.role)
            user_scope_mapping.scope_id = data.get('scope_id', user_scope_mapping.scope_id)
            db.session.commit()
            return {
                'message': 'User user_scope_mapping updated successfully.',
                'is_successful': True
            }

        # check if the user already has a user_scope_mapping for the scope
        user_scope_mapping_check = UserScopeMapping.query.filter(
            (UserScopeMapping.users.any(id=data.get('user_id', None)) &
            (UserScopeMapping.scope_id == data.get('scope_id', None)))
        ).first()
        if user_scope_mapping_check:
            return {
                'message': 'User already has the user_scope_mapping {} for scope ID: {}. Please edit user_scope_mapping ID: {} instead' \
                    .format(user_scope_mapping_check.role, user_scope_mapping_check.scope_id, 
                                                                        user_scope_mapping_check.id),
                'user_scope_mapping_id': user_scope_mapping_check.id,
                'is_successful': False
            }

        # Make sure the user has permissions for the scope in question before adding a user_scope_mapping
        if not g.user.can.modify.scope_id(data.get('scope_id', None)):
            return abort(401)
        if not data.get('role', None) in Config.APPROVED_ROLES:
            return {
                'message': 'Role must be in {}'.format(str(Config.APPROVED_ROLES)),
                'is_successful': False
            }
        user_scope_mapping = UserScopeMapping().create(role=data.get('role', None), 
                                                       scope_id=data.get('scope_id', None))
        user.user_scope_mappings.append(user_scope_mapping)
        db.session.commit()

        return {
            'message': 'UserScopeMapping added successfully.',
            'user_scope_mapping_id': user_scope_mapping.id,
            'is_successful': True
        }

    @auth.login_required
    def delete(self, user_scope_mapping_id=None):
        if not g.user.can.delete.user_scope_mapping_id(user_scope_mapping_id):
            return abort(401)
        user_scope_mapping = UserScopeMapping.query.filter_by(id=user_scope_mapping_id).first()
        if not user_scope_mapping:
            return {
                'message': 'User scope mapping does not exist',
                'is_successful': False
            }
        if len(user_scope_mapping.users) > 1 and user_scope_mapping:
            return {
                'message': 'Cannot delete user_scope_mapping. Remove other users first.',
                'is_successful': False
            }
        else:
            user_scope_mapping.delete()
            return {
                'message': 'Scope deleted successfully.',
                'is_successful': True
            }


api.add_resource(UserScopeMappingApi,
                 '/userScopeMappings',
                 '/userScopeMappings/<int:user_scope_mapping_id>',
                 '/userScopeMappings/byScopeId/<int:scope_id>',
                 '/userScopeMappings/byCategoryId/<int:category_id>',
                 '/userScopeMappings/byUserId/<int:user_id>')
