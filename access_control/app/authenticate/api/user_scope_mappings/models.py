# -*- coding: utf-8 -*-
from authenticate.utils import serialize_object
from authenticate.database import Column, Model, SurrogatePK, db, reference_col, relationship
import datetime as dt


class UserScopeMapping(SurrogatePK, Model):
    """A user_scope_mapping for a user."""

    __tablename__ = 'user_scope_mappings'
    role = Column(db.String(80), nullable=False)
    scope_id = reference_col('scopes', nullable=False)
    scope = relationship('Scope', backref='user_scope_mappings')
    created_on = Column(db.DateTime, default=dt.datetime.now())
    last_update = Column(db.DateTime, onupdate=dt.datetime.now())

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    @property
    def serialized(self):
        return serialize_object(self, self.__class__)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<UserScopeMapping({role} on {scope})>'.format(role=self.role, scope=self.scope)