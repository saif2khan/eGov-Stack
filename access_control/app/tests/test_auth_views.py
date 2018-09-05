# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""

from authenticate.api.user.models import User

from .factories import UserFactory
from .conftest import basic_auth_header


class TestAuthApi:
    """Login."""

    def test_incorrect_url_returns_404(self, user, testapp):
        res = testapp.get('/', headers=basic_auth_header(user, 'myprecious'), status=404)
        assert res.status_code == 404
        

    def test_can_get_auth_token_and_use_it(self, user, testapp):
        """Can get auth token and then use the token."""
        res = testapp.get('/api/v1/auth/token', headers=basic_auth_header(user.username, 'myprecious'))
        assert res.json.get('token', False)
        res = testapp.get('/api/v1/auth/token', headers=basic_auth_header(res.json.get('token'), ''))
        assert res.json.get('token', False)

    def test_can_get_auth_token_and_then_invalidate_it(self, user, testapp):
        """Can get auth token and then use the token."""
        res = testapp.get('/api/v1/auth/token', headers=basic_auth_header(user.username, 'myprecious'))
        assert res.json.get('token', False)
        res = testapp.get('/api/v1/auth/token', headers=basic_auth_header(res.json.get('token'), ''))
        assert res.json.get('token', False)

        token = res.json.get('token')

        res = testapp.get('/api/v1/auth/logout', headers=basic_auth_header(token, ''))
        assert res.json.get('message', False) == 'You have been logged out'

        res = testapp.get('/api/v1/auth/token', headers=basic_auth_header(token, ''), expect_errors=True)
        assert res.status_code == 401


    def test_bad_username_or_password_rejected(self, user, testapp):
        res = testapp.get('/api/v1/auth/token', headers=basic_auth_header(user.username, 'lalalala'), status=401)
        assert res.status_code == 401
        res = testapp.get('/api/v1/auth/token', headers=basic_auth_header('nonexistentuser', 'myprecious'), status=401)
        assert res.status_code == 401

    def test_reset_password(self, user, testapp):
        res = testapp.get('/api/v1/public-auth/reset-password?email=test@test.com')
        assert res.json.get('message') == 'Password reset initiated'

    def test_verify_email_token_works(self, user, testapp):
        assert user.email_verified == False
        token = user.generate_auth_token()
        res = testapp.get('/api/v1/public-auth/verify-email?token={}'.format(token))
        assert res.json.get('message') == 'Email verified'
        assert user.email_verified == True

    def test_reset_password(self, user, testapp):
        token = user.generate_auth_token()
        assert not user.check_password('testt')
        assert user.check_password('myprecious')
        res = testapp.post('/api/v1/public-auth/reset-password?token={}'.format(token), {
            'password': 'testt'
        })
        assert user.check_password('testt')
        assert res.json.get('message') == 'User updated successfully'

        res = testapp.post('/api/v1/public-auth/reset-password?token={}'.format('badtoken'), {
            'password': 'testt22'
        })
        assert res.json.get('message') == 'Invalid token'
        assert user.check_password('testt')




