# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from authenticate.api.user.models import User
from authenticate.extensions import db

from .factories import UserFactory
from .conftest import basic_auth_header


class TestUserApi:

    def test_can_get_list_of_users(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/users', headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert len(res.json.get('users')) == 2

        # Make sure non root admin can only see users he has permission to see, in this case one
        res = testapp.get('/api/v1/users', headers=basic_auth_header(user.username, 'myprecious'))

        assert res.status_code == 200
        assert len(res.json.get('users')) == 1

    def test_can_get_list_of_users_2(self, user, root_admin_user, testapp):
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

        # Make sure non root admin can only see users he has permission to see, in this case one
        res = testapp.get('/api/v1/users', headers=basic_auth_header(user.username, 'yes'))

        assert res.status_code == 200
        assert len(res.json.get('users')) == 1

    def test_get_user_by_id(self, user, root_admin_user, testapp):
        root_admin_user.username = 'cheese'
        res = testapp.get('/api/v1/user/{}'.format(root_admin_user.id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('username', False) == 'cheese'

    def test_root_user_flag_set_true(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/user/{}'.format(root_admin_user.id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('is_root_admin', False) == True

    def test_root_user_flag_set_false(self, user, root_admin_user, testapp):
        res = testapp.get('/api/v1/user/{}'.format(user.id), headers=basic_auth_header(user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('is_root_admin', False) == False

    def test_create_user_no_phone_number(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWodddo',
            'email': 'dan@danwddins.com',
            'first_name': 'bob',
            'last_name': 'sanders',
            'password': '6867476362'
        })

        assert res.status_code == 200
        assert res.json.get('message', False) == 'All fields are required'

    def test_create_user_invalid_email(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWodddo',
            'email': 'a%40a11',
            'first_name': 'bob',
            'last_name': 'sanders',
            'password': '6867476362',
            'mobile_number': '123'
        })

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Email address not valid'

    def test_create_user_invalid_phone_number(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWodddo',
            'email': 'dan@danwddins.com',
            'password': '6867476362',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123aaa'
        })

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Invalid phone number'

    def test_update_password(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWodddo',
            'email': 'dan@danwddins.com',
            'password': '6867476362',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123'
        })

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User added successfully.'
        assert res.json.get('user_id', False)

        user = User.query.filter_by(id=res.json.get('user_id')).first()

        res = testapp.post('/api/v1/user/{}'.format(user.id), {
            'password': 'TestWoot',
            'username': 'new',
            'email': 'dan@theman.com',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        print(res)

        assert user.check_password('TestWoot')

    def test_create_new_user(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWodddo',
            'email': 'dan@danwddins.com',
            'mobile_number': '6867476362',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123',
            'password': 'yes'
        })

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User added successfully.'
        assert res.json.get('user_id', False)

        res = testapp.post('/api/v1/users', {
            'username': 'TestWoo',
            'mobile_number': '6867476362',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123',
            'password': 'yes',
            'email': 1
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Email address not valid'


        res = testapp.post('/api/v1/users', {
            'username': 'TestWoo',
            'mobile_number': '23423423423',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123',
            'password': 'yes',
            'email': 'asdfasd@sdfsdf.com'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User added successfully.'

    def test_edit_user_2(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWoo',
            'email': 'dan@danwddins.com',
            'mobile_number': '6867476362',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123',
            'password': 'yes'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User added successfully.'

        # Need to attach the user to a user that the user has permission
        # on in order to update it
        user_id = res.json.get('user_id')

        res = testapp.post('/api/v1/user/{}'.format(user_id), {
            'username': 'TestWoot',
            'email': 'dan@danwinsdddd.com',
            'mobile_number': '8688583718'
        }, expect_errors=True)

        assert res.status_code == 401
        assert res.json.get('message', False) == 'Unable to authenticate request'

    def test_edit_user(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWoo',
            'email': 'dan@danwddins.com',
            'mobile_number': '6867476362',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123',
            'password': 'yes'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User added successfully.'

        # Need to attach the user to a user that the user has permission
        # on in order to update it
        user_id = res.json.get('user_id')

        res = testapp.post('/api/v1/user/{}'.format(user_id), {
            'username': 'TestWoot',
            'email': 'dan@danwinsdddd.com',
            'mobile_number': '8688583718'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User updated successfully.'
        
        user = User.query.filter_by(id=user_id).first()

        assert user.username == 'TestWoot'
        assert user.email == 'dan@danwinsdddd.com'
        assert user.mobile_number == '8688583718'

        res = testapp.post('/api/v1/user/{}'.format(user_id), {
            'mobile_number': '3333333'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert user.mobile_number == '3333333'

        res = testapp.post('/api/v1/user/{}'.format(user_id), {
            'password': '66'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert user.check_password('66')

        res = testapp.post('/api/v1/user/{}'.format(user_id), {
            'email': 'lele@sdfdsf.com'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert user.email == 'lele@sdfdsf.com'

        res = testapp.post('/api/v1/user/{}'.format(user_id), {
            'username': 'billjoel'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert user.username == 'billjoel'

    def test_delete_user(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/users', {
            'username': 'TestWoo',
            'email': 'dan@danwddins.com',
            'mobile_number': '6867476362',
            'first_name': 'bob',
            'last_name': 'sanders',
            'mobile_number': '123',
            'password': 'yes'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'User added successfully.'
        assert res.json.get('user_id', False)

        user_id = res.json.get('user_id')
    
        res = testapp.delete('/api/v1/user/{}'.format(user_id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        user = User.query.filter_by(id=user_id).first()

        assert user.is_deleted == True
        assert user is not None
