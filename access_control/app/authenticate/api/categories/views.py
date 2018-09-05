# -*- coding: utf-8 -*-
from flask_restful import Resource, inputs, reqparse
from flask import Flask, jsonify, request, g
from authenticate.utils import abort
from authenticate.extensions import api, db, auth
from authenticate.settings import Config
from authenticate.api.user.models import User
from authenticate.api.categories.models import Category
import datetime as dt

parser = reqparse.RequestParser(bundle_errors=True)


class CategoryApi(Resource):
    @auth.login_required
    def get(self, category_id=None):

        if not category_id:
            categories = Category.query.all()
            return {
                'categories': [category.serialized for category in 
                            list(filter(lambda d: g.user.can.view.category_id(d.id), categories))],
                'is_successful': True
            }

        category = Category.query.filter_by(id=category_id).first()
        if g.user.can.view.category_id(category.id):
            return category.serialized  
        else:
            return abort(401)

    @auth.login_required
    def post(self, category_id=None):
        data = request.values

        if data.get('id', category_id):
            if not g.user.can.modify.category_id(data.get('id', category_id)):
                return abort(401)
            category_check = Category.query.filter(
                (Category.name == data.get('name', None)) &
                (Category.id != data.get('id', None))
            ).first()
            if category_check:
                return {
                    'message': 'Category name already in use under category ID {}' \
                        .format(category_check.id),
                    'is_successful': False
                }
            category = Category.query.filter_by(id=data.get('id', category_id)).first()
            if not category:
                return {
                    'message': 'Category does not exist',
                    'is_successful': False
                }
            category.name = data.get('name', category.name)
            db.session.commit()
            return {
                'message': 'Category updated successfully.',
                'is_successful': True
            }

        category_check = Category.query.filter_by(name=data.get('name', category_id)).first()
        if category_check:
            return {
                'message': 'Category name already in use under category ID {}' \
                    .format(category_check.id),
                'is_successful': False
            }
        category = Category().create(name=data.get('name', None))

        db.session.commit()

        return {
            'message': 'Category added successfully.',
            'category_id': category.id,
            'is_successful': True
        }

    @auth.login_required
    def delete(self, category_id=None):
        if not g.user.can.delete.category_id(category_id):
            return abort(401)
        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return {
                'message': 'Category does not exist',
                'is_successful': False
            }
        if category.scopes:
            return {
                'message': 'Cannot delete category. Please remove all attached scopes first.',
                'is_successful': False
            }
        else:
            category.delete()
            return {
                'message': 'Category deleted successfully.',
                'is_successful': True
            }
            


api.add_resource(CategoryApi,
                 '/categories',
                 '/categories/<int:category_id>')
