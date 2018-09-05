# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""

from authenticate.api.user.models import User
from authenticate.settings import TestConfig
from flask.testing import FlaskCliRunner
from .factories import UserFactory
from .conftest import basic_auth_header
from authenticate.commands import initial_setup


class TestCommands:
    """Initial setup"""

    def test_initial_setup(self, user, testapp):
        from authenticate.app import create_app
        app = create_app(TestConfig)
        runner = FlaskCliRunner(app)
        # invoke the command directly
        result = runner.invoke(initial_setup, ['--username', 'root_admin', '--password', 'myprecious', '--email', 'root@precious.com'])

        assert 'Root user and root scope setup successfully' in result.output

        user = User.query.filter_by(email='root@precious.com').first()
        assert user.username == 'root_admin'
        assert user.check_password('myprecious')
        assert user.email == 'root@precious.com'