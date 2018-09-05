# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from authenticate.api.user.models import User
from authenticate.api.categories.models import Category
from authenticate.api.scopes.models import Scope
from authenticate.extensions import db

from .factories import UserFactory, AppContextFactory, CategoryFactory, RootScopeFactory
from .conftest import basic_auth_header


class TestCategoryApi:

    def test_can_get_list_of_categories(self, user, root_admin_user, testapp):
        category = CategoryFactory(name='TestCategory')
        db.session.commit()

        scope = root_admin_user.user_scope_mappings[0].scope
        scope.category_id = category.id
        db.session.commit()
        
        res = testapp.get('/api/v1/categories', headers=basic_auth_header(root_admin_user.username, 'myprecious'))
        # print(res)
        assert res.status_code == 200
        assert res.json.get('categories', False)
        # Make sure non root admin can only see categories he has permission to see, in this case zero
        res = testapp.get('/api/v1/categories', headers=basic_auth_header(user.username, 'myprecious'))

        assert res.status_code == 200
        assert not res.json.get('categories', False)

    def test_get_category_by_id(self, user, root_admin_user, testapp):
        category = CategoryFactory(name='TestCategory')
        db.session.commit()

        scope = root_admin_user.user_scope_mappings[0].scope
        scope.category_id = category.id
        db.session.commit()

        res = testapp.get('/api/v1/categories/{}'.format(category.id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('name', False) == 'TestCategory'

    def test_create_new_category(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/categories', {
            'name': 'TestWoo'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Category added successfully.'
        assert res.json.get('category_id', False)

    def test_edit_category(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/categories', {
            'name': 'TestWoo'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Category added successfully.'
        assert res.json.get('category_id', False)

        # Need to attach the category to a scope that the user has permission
        # on in order to update it
        category_id = res.json.get('category_id')
        scope = root_admin_user.user_scope_mappings[0].scope
        scope.category_id = category_id
        db.session.commit()

        res = testapp.post('/api/v1/categories/{}'.format(category_id), {
            'name': 'TestWoot'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Category updated successfully.'
        
        category = Category.query.filter_by(id=category_id).first()

        assert category.name == 'TestWoot'

    def test_delete_category(self, user, root_admin_user, testapp):
        category = CategoryFactory(name='TestCategory')
        db.session.commit()

        scope = root_admin_user.user_scope_mappings[0].scope
        scope.category_id = category.id
        db.session.commit()

        category_id = category.id

        res = testapp.delete('/api/v1/categories/{}'.format(category_id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.json.get('message') == 'Cannot delete category. Please remove all attached scopes first.'

        category.scopes = []
        db.session.commit()

        res = testapp.delete('/api/v1/categories/{}'.format(category_id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        category = Category.query.filter_by(id=category_id).first()

        assert category == None