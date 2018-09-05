# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from webtest import TestApp

from authenticate.app import create_app
from authenticate.api.scopes.models import Scope
from authenticate.database import db as _db
from authenticate.settings import TestConfig
from requests.auth import _basic_auth_str

from .factories import UserFactory, RootScopeFactory, UserScopeMappingFactory

def basic_auth_header(username, password):
    return {
        'Authorization': _basic_auth_str(username, password)
    }


@pytest.fixture
def app():
    """An application for the tests."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.fixture
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """A user for the tests."""
    user = UserFactory(password='myprecious')
    root_scope = RootScopeFactory(name='Root')
    db.session.commit()
    return user

@pytest.fixture
def root_admin_user(db):
    """A user for the tests."""
    user = UserFactory(password='myprecious')
    root_scope = Scope.query.filter_by(parent_scope_id=None).first()
    db.session.commit()
    user_scope_mapping = UserScopeMappingFactory(role='ADMIN')
    user_scope_mapping.scope_id = root_scope.id
    user.user_scope_mappings.append(user_scope_mapping)
    
    db.session.commit()
    return user
