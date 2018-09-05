# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
from datetime import timedelta
from itertools import chain

from flask_login import UserMixin

from authenticate.utils import serialize_object
from authenticate.database import Column, Model, SurrogatePK, db, reference_col, relationship
from authenticate.extensions import bcrypt
from authenticate.api.scopes.models import Scope
from authenticate.api.user_scope_mappings.models import UserScopeMapping
from authenticate.api.categories.models import Category
from authenticate.settings import Config
from itsdangerous import URLSafeTimedSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from sqlalchemy.orm import foreign, remote, backref


rel_users_user_scope_mappings = db.Table(
    'users_user_scope_mappings',
    db.Column('user_scope_mapping_id', db.Integer, db.ForeignKey('user_scope_mappings.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    first_name = Column(db.String(80))
    last_name = Column(db.String(80))
    mobile_number = Column(db.String(80))
    created_on = Column(db.DateTime, default=dt.datetime.now())
    last_update = Column(db.DateTime, onupdate=dt.datetime.now())
    is_deleted = Column(db.Boolean, default=False)
    email_verified = Column(db.Boolean, default=False)
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.Binary(128), nullable=True)
    user_scope_mappings = relationship("UserScopeMapping",
                         secondary=rel_users_user_scope_mappings,
                         backref="users")
    app_user = False


    def __init__(self, password=None, app_user=False, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

        """If a new user object is created as an app_user like `user = User(app_user=True)`
        then this user will automatically have root admin permissions. This user cannot
        be saved to the database and only exists for the length of a request. It is a 'Ghost'
        user designed to give an application the same kind of permission calls as a regular
        user without needing to store it in the database."""
        self.app_user = app_user


    def traverse_up_tree_from_node(self, starting_node):
        """Starting at the `starting_node` we walk up the node (scope) tree
        by calling `starting_node.parent` to go up one level checking for
        the correct permission at each level. If nothing is found by the time
        we reach the root node (no parent) then we return False as the permission
        doesn't exist."""
        for user_scope_mapping in starting_node.user_scope_mappings:
            for user in user_scope_mapping.users:
                if user == self and user_scope_mapping.role in self.permission_types:
                    print(user, 'has permission on', starting_node)
                    return True
        if starting_node.parent:
            return self.traverse_up_tree_from_node(starting_node.parent)
        else:
            return False

    @property
    def is_root_admin(self):
        root_scope = Scope.query.filter_by(parent_scope_id=None).first()
        for user_scope_mapping in root_scope.user_scope_mappings:
            for user in user_scope_mapping.users:
                if user == self:
                    return True
        return self.app_user or False

    @property
    def can(self):
        self.permission_types = []
        return self

    @property
    def view(self):
        self.permission_types = ['READ', 'READ-WRITE', 'ADMIN']
        return self

    @property
    def modify(self):
        self.permission_types = ['READ-WRITE', 'ADMIN']
        return self

    @property
    def delete(self):
        self.permission_types = ['ADMIN']
        return self

    def user_id(self, _user_id):
        """If a user has no user_scope_mappings for any scope they are 'free-floating' users
        and only super admins and the user themself should be able to edit them or view 
        them. If a user has at least one user_scope_mapping then we can look at all of their 
        user_scope_mappings and check to see that we have permission in at least one of those 
        user_scope_mappings to do the requested action."""

        # Must be admin to do anything with users
        self.permission_types = ['ADMIN']

        user = self.query.filter_by(id=_user_id).first()

        if not self.is_root_admin:
            if self == user:
                return True
            else:
                return False


        # Free floating user
        if not user.user_scope_mappings:
            # Users can always have access to themselves
            if user == self:
                return True
            # ADMIN users on the root node can also have access 
            for user_scope_mapping in self.user_scope_mappings:
                # user has access to the root node with the correct permission
                if not user_scope_mapping.scope.parent and user_scope_mapping.role in \
                                                                            self.permission_types:
                    return True
                else:
                    return False

        user_scope_mappings_with_permission = []
        for user_scope_mapping in user.user_scope_mappings:
            if self.traverse_up_tree_from_node(user_scope_mapping.scope):
                user_scope_mappings_with_permission.append(user_scope_mapping.scope)
        return self.app_user or (True if user_scope_mappings_with_permission else False)

    def user_scope_mapping_id(self, _user_scope_mapping_id):
        """Start with the user_scope_mapping to be modified, and use the attached scope as
        the starting scope for determining permission to modify the user_scope_mapping."""

        # Must be admin to do anything with user_scope_mappings
        self.permission_types = ['ADMIN']

        user_scope_mapping = UserScopeMapping.query.filter_by(id=_user_scope_mapping_id).first()
        if not user_scope_mapping:
            return False

        if self.id in [user.id for user in user_scope_mapping.users]:
            return True

        return self.app_user or self.traverse_up_tree_from_node(user_scope_mapping.scope)

    def scope_id(self, _scope_id):
        """Start with the scope to be read/modified/deleted and go up the tree
        looking for permissions on the target scope or any parent. The _scope_id
        passed in here is the parent scope of whatever scope is being modified."""

        # Must be admin to do anything with scopes
        self.permission_types = ['ADMIN']

        scope = Scope.query.filter_by(id=_scope_id).first()
        # Scope must always have a parent unless it is the root scope
        if not scope:
            return False
        return self.app_user or self.traverse_up_tree_from_node(scope)

    def category_id(self, _category_id):
        """The approach here is to find every scope that is being used by the
        category in question. The user would have to have the right permission
        on every scope attached to the category in orer to modify/read/delete 
        the category."""
        category = Category.query.filter_by(id=_category_id).first()
        scopes_with_permission = []
        if not category.scopes:
            return self.app_user or self.is_root_admin
        for scope in category.scopes:
            if self.traverse_up_tree_from_node(scope):
                scopes_with_permission.append(scope)
        return self.app_user or scopes_with_permission


    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def generate_auth_token(self):
        s = Serializer(Config.SECRET_KEY)
        return s.dumps(self.email, salt='recover-key')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            email = s.loads(token, salt="recover-key", max_age=3600)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        return User.query.filter_by(email=email).first()

    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name)

    @property
    def serialized(self):
        return serialize_object(self, self.__class__,
                                is_root_admin=self.is_root_admin)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)
