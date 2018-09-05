# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from authenticate.api.user.models import User
from authenticate.api.categories.models import Category
from authenticate.api.scopes.models import Scope
from authenticate.extensions import db

from .factories import UserFactory, AppContextFactory, RootScopeFactory
from .conftest import basic_auth_header


class TestScopeApi:

    def test_can_get_list_of_scopes(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/scopes', headers=basic_auth_header(root_admin_user.username, 'myprecious'))
        # print(res)
        assert res.status_code == 200
        assert res.json.get('scopes', False)
        # Make sure non root admin can only see scopes he has permission to see, in this case zero
        res = testapp.get('/api/v1/scopes', headers=basic_auth_header(user.username, 'myprecious'))

        assert res.status_code == 200
        assert not res.json.get('scopes', False)

    def test_get_scope_by_id(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/scopes/{}'.format(1), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('name', False) == 'Root'

    def test_create_new_scope_bad_category(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/scopes', {
            'name': 'TestWoo',
            'parent_scope_id': 1,
            'category_id': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Category does not exist - cannot add scope'

    def test_create_new_scope(self, user, root_admin_user, testapp):
        category = Category()
        category.name = 'test'
        db.session.add(category)
        db.session.commit()
        res = testapp.post('/api/v1/scopes', {
            'name': 'TestWoo',
            'parent_scope_id': 1,
            'category_id': category.id
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Scope added successfully.'
        assert res.json.get('scope_id', False)

    def test_create_new_scope_2(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/scopes', {
            'name': 'Testing1',
            'parent_scope_id': 2,
            'category_id': 5
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Invalid parent scope'

    def test_create_new_scope_has_valid_parent(self, user, root_admin_user, testapp):
        category = Category()
        category.name = 'test'
        db.session.add(category)
        db.session.commit()
        res = testapp.post('/api/v1/scopes', {
            'name': 'TestWoo',
            'parent_scope_id': 1,
            'category_id': category.id
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Scope added successfully.'
        assert res.json.get('scope_id', False)

        scope_id = res.json.get('scope_id', False)
        

        res = testapp.post('/api/v1/scopes/{}'.format(scope_id), {
            'name': 'TestWoot',
            'parent_scope_id': scope_id
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        scope = Scope.query.filter_by(id=scope_id).first()

        assert scope.name == 'TestWoo'
        assert scope.id != scope.parent_scope_id

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Invalid parent scope'

        res = testapp.post('/api/v1/scopes', {
            'name': 'CrazyParent',
            'parent_scope_id': 55
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Invalid parent scope'


    def test_edit_scope(self, user, root_admin_user, testapp):
        category = Category()
        category.name = 'test'
        db.session.add(category)
        db.session.commit()
        res = testapp.post('/api/v1/scopes', {
            'name': 'TestWoo',
            'parent_scope_id': 1,
            'category_id': category.id
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Scope added successfully.'
        assert res.json.get('scope_id', False)

        # Need to attach the scope to a scope that the user has permission
        # on in order to update it
        scope_id = res.json.get('scope_id')

        res = testapp.post('/api/v1/scopes/{}'.format(scope_id), {
            'name': 'TestWoot',
            'parent_scope_id': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Scope updated successfully.'
        
        scope = Scope.query.filter_by(id=scope_id).first()

        assert scope.name == 'TestWoot'

    def test_delete_scope(self, user, root_admin_user, testapp):
        category = Category()
        category.name = 'test'
        db.session.add(category)
        db.session.commit()
        res = testapp.post('/api/v1/scopes', {
            'name': 'TestWoo',
            'parent_scope_id': 1,
            'category_id': category.id
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Scope added successfully.'
        assert res.json.get('scope_id', False)

        scope_id = res.json.get('scope_id')
    
        res = testapp.delete('/api/v1/scopes/{}'.format(scope_id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        scope = Scope.query.filter_by(id=scope_id).first()

        assert scope == None