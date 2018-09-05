# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from flask import url_for

from authenticate.api.user.models import User
from authenticate.api.app_contexts.models import AppContext
from authenticate.extensions import db

from .factories import UserFactory, AppContextFactory, ApplicationFactory
from .conftest import basic_auth_header


class TestAppContextApi:

    def test_can_get_list_of_app_contexts(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')
        test_context = AppContextFactory(name='TestContext')
        test_context.application_id = application.id
        res = testapp.get('/api/v1/appContexts', headers=basic_auth_header(root_admin_user.username, 'myprecious'))
        # print(res)
        assert res.status_code == 200
        assert res.json.get('app_contexts', False)
        # Make sure non root admin is denied access
        res = testapp.get('/api/v1/appContexts', headers=basic_auth_header(user.username, 'myprecious'), status=401)

        assert res.status_code == 401
        assert not res.json.get('app_contexts', False)

    def test_get_app_context_by_id(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')
        test_context = AppContextFactory(name='TestContext')
        test_context.application_id = application.id
        db.session.commit()
        res = testapp.get('/api/v1/appContexts/{}'.format(test_context.id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('context_credentials', False)

    def test_create_new_app_context(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')
        db.session.commit()
        res = testapp.post('/api/v1/appContexts', {
            'application_id': application.id,
            'context_credentials': '{"amazon": "s3"}',
            'name': 'TestWoo'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'AppContext added successfully.'
        assert res.json.get('app_context_id', False)

    def test_edit_app_context(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')
        db.session.commit()
        res = testapp.post('/api/v1/appContexts', {
            'application_id': application.id,
            'context_credentials': '{"amazon": "s3"}',
            'name': 'TestWoo'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'AppContext added successfully.'
        assert res.json.get('app_context_id', False)

        app_context_id = res.json.get('app_context_id')

        res = testapp.post('/api/v1/appContexts/{}'.format(app_context_id), {
            'application_id': application.id,
            'context_credentials': '{"amazon": "s4"}',
            'name': 'TestWoot'
        }, headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        assert res.status_code == 200
        assert res.json.get('message', False) == 'AppContext updated successfully.'
        
        app_ctx = AppContext.query.filter_by(id=app_context_id).first()

        assert app_ctx.name == 'TestWoot'
        assert app_ctx.context_credentials == {'amazon': 's4'}

    def test_delete_app_context(self, user, root_admin_user, testapp):
        application = ApplicationFactory(name='TestApplication')
        test_context = AppContextFactory(name='TestContext')
        test_context.application_id = application.id
        db.session.commit()

        app_ctx_id = test_context.id

        res = testapp.delete('/api/v1/appContexts/{}'.format(app_ctx_id), headers=basic_auth_header(root_admin_user.username, 'myprecious'))

        app_ctx = AppContext.query.filter_by(id=app_ctx_id).first()

        assert app_ctx == None

