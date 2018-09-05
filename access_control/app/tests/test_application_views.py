# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from authenticate.api.user.models import User
from authenticate.api.applications.models import Application
from authenticate.extensions import db

from .factories import UserFactory, AppContextFactory, ApplicationFactory
from .conftest import basic_auth_header


class TestApplicationApi:

    def test_can_get_list_of_applications(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')
        res = testapp.get('/api/v1/applications', headers=basic_auth_header(root_admin_user.username, 'myprecious'))
        # print(res)
        assert res.status_code == 200
        assert res.json.get('applications', False)
        # Make sure non root admin is denied access
        res = testapp.get('/api/v1/applications', headers=basic_auth_header(user.username, 'myprecious'), status=401)

        assert res.status_code == 401
        assert not res.json.get('applications', False)

    def test_get_application_by_id(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')

        db.session.commit()
        res = testapp.get('/api/v1/applications/{}'.format(application.id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('name', False) == 'TestApplication'

    def test_create_new_application(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/applications', {
            'white_listed_ips': '["127.0.0.1"]',
            'name': 'TestWoo'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        print(res, 'lalal')

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Application added successfully.'
        assert res.json.get('application_id', False)

    def test_edit_application(self, user, root_admin_user, testapp):
        res = testapp.post('/api/v1/applications', {
            'white_listed_ips': '["127.0.0.1"]',
            'name': 'TestWoo'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Application added successfully.'
        assert res.json.get('application_id', False)

        application_id = res.json.get('application_id')

        res = testapp.post('/api/v1/applications/{}'.format(application_id), {
            'white_listed_ips': '["127.0.0.2"]',
            'name': 'TestWoot'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'Application updated successfully.'
        
        application = Application.query.filter_by(id=application_id).first()

        assert application.name == 'TestWoot'
        assert application.white_listed_ips == ['127.0.0.2']

    def test_delete_application(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')
        db.session.commit()

        application_id = application.id

        res = testapp.delete('/api/v1/applications/{}'.format(application_id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        application = Application.query.filter_by(id=application_id).first()

        assert application == None