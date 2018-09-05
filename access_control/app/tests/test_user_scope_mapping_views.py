# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from authenticate.api.user.models import User
from authenticate.api.user_scope_mappings.models import UserScopeMapping
from authenticate.extensions import db
from authenticate.settings import Config

from .factories import UserFactory, AppContextFactory, RootScopeFactory, UserScopeMappingFactory
from .conftest import basic_auth_header


class TestUserScopeMappingApi:

    def test_can_get_list_of_user_scope_mappings(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/userScopeMappings', headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('user_scope_mappings', False)

        # Make sure non root admin can only see user_scope_mappings he has permission to see, in this case zero
        res = testapp.get('/api/v1/userScopeMappings', headers=basic_auth_header(user.username, 'myprecious'))

        assert res.status_code == 200
        assert not res.json.get('user_scope_mappings', False)

    def test_can_get_list_of_user_scope_mappings_2(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWoo',
            'email': 'dan@danwindddds.com',
            'mobile_number': '8688583716',
            'first_name': 'bob',
            'last_name': 'sanders',
            'password': 'yes'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User added successfully.'

        user = User.query.filter_by(email='dan@danwindddds.com').first()
        scope_mapping = UserScopeMapping()
        scope_mapping.role = 'READ'
        scope_mapping.scope_id = 2
        user.user_scope_mappings.append(scope_mapping)
        db.session.commit()

        # Make sure non root admin can only see users he has permission to see, in this case one
        res = testapp.get('/api/v1/userScopeMappings', headers=basic_auth_header(user.username, 'yes'))
        print(res.json.get('user_scope_mappings', False))
        assert res.status_code == 200
        assert len(user.user_scope_mappings) == 1
        assert user.id in [u.id for u in scope_mapping.users]
        assert len(res.json.get('user_scope_mappings', False)) == 1
        assert res.json.get('user_scope_mappings')[0]['scope_id'] == 2

    def test_get_user_scope_mappings_by_id(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/userScopeMappings/{}'.format(1), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('role', False) == 'ADMIN'

    def test_get_user_scope_mappings_by_scope_id(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/userScopeMappings/byScopeId/{}'.format(1), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('user_scope_mappings', False)

    def test_get_user_scope_mappings_by_user_id(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/userScopeMappings/byUserId/{}'.format(root_admin_user.id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('user_scope_mappings', False)
        assert len(res.json.get('user_scope_mappings')) == len(root_admin_user.user_scope_mappings)

    def test_get_user_scope_mappings_by_category_id(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/userScopeMappings/byCategoryId/{}'.format(1), headers=basic_auth_header(root_admin_user.username, 'myprecious'))
        
        assert res.status_code == 200
        assert not res.json.get('user_scope_mappings', False)

    def test_create_new_user_scope_mappings(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/userScopeMappings', {
            'role': 'TestWoo',
            'scope_id': 1,
            'user_id': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.json.get('message', False) == 'Role must be in {}'.format(str(Config.APPROVED_ROLES))

        res = testapp.post('/api/v1/userScopeMappings', {
            'role': 'READ',
            'scope_id': 1,
            'user_id': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.json.get('message', False) == 'UserScopeMapping added successfully.'
        assert res.json.get('user_scope_mapping_id', False)

    def test_edit_user_scope_mappings_for_non_existant_scope(self, user, root_admin_user, testapp):

        res = testapp.post('/api/v1/userScopeMappings/223423', {
            'role': 'READ',
            'scope_id': 124234234234234,
            'user_id': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'), expect_errors=True)

        assert res.status_code == 401

    def test_edit_scope(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/userScopeMappings', {
            'role': 'READ',
            'scope_id': 1,
            'user_id': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.json.get('message', False) == 'UserScopeMapping added successfully.'
        assert res.json.get('user_scope_mapping_id', False)

        user_scope_mapping_id = res.json.get('user_scope_mapping_id')

        res = testapp.post('/api/v1/userScopeMappings/{}'.format(user_scope_mapping_id), {
            'role': 'READ-WRITE',
            'user_id': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User user_scope_mapping updated successfully.'
        
        usr_scp_map = UserScopeMapping.query.filter_by(id=user_scope_mapping_id).first()

        assert usr_scp_map.role == 'READ-WRITE'

    # def test_delete_scope(self, user, root_admin_user, testapp):
    #     res = testapp.post('/api/v1/userScopeMappings', {
    #         'name': 'TestWoo',
    #         'parent_scope_id': 1
    #     }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

    #     assert res.status_code == 201
    #     assert res.json.get('message', False) == 'UserScopeMapping added successfully.'
    #     assert res.json.get('scope_id', False)

    #     scope_id = res.json.get('scope_id')
    
    #     res = testapp.delete('/api/v1/userScopeMappings/{}'.format(scope_id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

    #     scope = UserScopeMapping.query.filter_by(id=scope_id).first()

    #     assert scope == None