# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from authenticate.database import db
from authenticate.api.user.models import User
from authenticate.api.scopes.models import Scope
from authenticate.api.app_contexts.models import AppContext
from authenticate.api.applications.models import Application
from authenticate.api.user_scope_mappings.models import UserScopeMapping
from authenticate.api.categories.models import Category


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    username = Sequence(lambda n: 'user{0}'.format(n))
    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = PostGenerationMethodCall('set_password', 'example')

    class Meta:
        """Factory configuration."""

        model = User

class RootScopeFactory(BaseFactory):
    """Creates a root scope."""

    name = Sequence(lambda n: 'scope{0}'.format(n))

    class Meta:
        """Factory configuration."""

        model = Scope

class AppContextFactory(BaseFactory):
    """Creates an app context."""

    name = Sequence(lambda n: 'scope{0}'.format(n))
    context_credentials = """{
        "amazon": "12345"
    }"""

    class Meta:
        """Factory configuration."""

        model = AppContext

class ApplicationFactory(BaseFactory):
    """Creates an application."""

    name = Sequence(lambda n: 'scope{0}'.format(n))

    class Meta:
        """Factory configuration."""

        model = Application

class CategoryFactory(BaseFactory):
    """Creates an application."""

    name = Sequence(lambda n: 'scope{0}'.format(n))

    class Meta:
        """Factory configuration."""

        model = Category


class UserScopeMappingFactory(BaseFactory):
    """Creates an application."""

    role = Sequence(lambda n: 'scope{0}'.format(n))

    class Meta:
        """Factory configuration."""

        model = UserScopeMapping
