# -*- coding: utf-8 -*-
from flask_restful import Resource, inputs, reqparse
from flask import Flask, jsonify, request, g
from authenticate.utils import abort
from authenticate.extensions import api, db, auth
from authenticate.settings import Config
from authenticate.api.user.models import User
from authenticate.api.scopes.models import Scope
from authenticate.api.categories.models import Category
import datetime as dt

parser = reqparse.RequestParser(bundle_errors=True)


class ScopesApi(Resource):
    @auth.login_required
    def get(self, scope_id=None):
        parser.add_argument('treeView', location='args')
        args = parser.parse_args()
        if not scope_id:
            if args.get('treeView', None):
                root_scope = Scope.query.filter_by(parent_scope_id=None).first()
                return {
                    'scopes': root_scope.tree_serialized(g.user),
                    'is_successful': True
                }
            else:
                scopes = Scope.query.all()
                return {
                    'scopes': [scope.serialized for scope in list(filter(lambda d: g.user.can.view.scope_id(d.id), scopes))],
                    'is_successful': True
                }

        scope = Scope.query.filter_by(id=scope_id).first()

        if g.user.can.view.scope_id(scope.id):
            return scope.serialized  
        else:
            return abort(401)

    @auth.login_required
    def post(self, scope_id=None):
        # print(request.values)
        data = request.values

        if data.get('id', scope_id):
            if not g.user.can.modify.scope_id(data.get('id', scope_id)):
                return abort(401)
            scope_check = Scope.query.filter(
                (Scope.name == data.get('name', None)) &
                (Scope.id != data.get('id', scope_id))
            ).first()
            if scope_check:
                return {
                    'message': 'Scope name already in use under scope ID {}'.format(scope_check.id),
                    'is_successful': False
                }
            
            scope = Scope.query.filter_by(id=data.get('id', scope_id)).first()
            if not scope:
                return {
                    'message': 'Scope does not exist',
                    'is_successful': False
                }
            parent_scope = Scope.query.filter_by(id=data.get('parent_scope_id', None)).first()
            if scope == parent_scope:
                return {
                    'message': 'Invalid parent scope',
                    'is_successful': False
                }
            scope.parent_scope_id = data.get('parent_scope_id', scope.parent_scope_id)
            scope.name = data.get('name', scope.name)
            scope.category_id = data.get('category_id', scope.category_id)
            category_check = Category.query.filter_by(id=scope.category_id).first()
            if not category_check:
                return {
                    'message': 'Category does not exist - cannot modify scope',
                    'is_successful': False
                }
            db.session.commit()

            return {
                'message': 'Scope updated successfully.',
                'is_successful': True
            }

        scope_check = Scope.query.filter_by(name=data.get('name', None)).first()
        if scope_check:
            return {
                'message': 'Scope name already in use under scope ID {}'.format(scope_check.id),
                'is_successful': False
            }

        # For new scopes, check to see if the user has access to the parent scope
        # before allowing them to create a new one
        parent_scope = Scope.query.filter_by(id=data.get('parent_scope_id', None)).first()
        if not data.get('parent_scope_id', None) \
            or not parent_scope:
            return {
                'message': 'Invalid parent scope',
                'is_successful': False
            }
        category_check = Category.query.filter_by(id=data.get('category_id', None)).first()
        if not category_check:
            return {
                'message': 'Category does not exist - cannot add scope',
                'is_successful': False
            }
        if not g.user.can.modify.scope_id(data.get('parent_scope_id', None)):
            return abort(401)
        scope = Scope().create(parent_scope_id=data.get('parent_scope_id', None),
                               name=data.get('name', None),
                               category_id=data.get('category_id', None))

        db.session.commit()

        return {
            'message': 'Scope added successfully.',
            'scope_id': scope.id
        }

    @auth.login_required
    def delete(self, scope_id=None):
        if not g.user.can.delete.scope_id(scope_id):
            return abort(401)
        scope = Scope.query.filter_by(id=scope_id).first()
        if not scope:
            return {
                'message': 'Scope does not exist',
                'is_successful': False
            }
        if scope.children or scope.user_scope_mappings:
            return {
                'message': ('Cannot delete scope. Please remove all attached roles and ', 
                            'children scopes first.')
            }
        else:
            scope.delete()
            return {
                'message': 'Scope deleted successfully.'
            }

api.add_resource(ScopesApi,
                 '/scopes',
                 '/scopes/<int:scope_id>')
