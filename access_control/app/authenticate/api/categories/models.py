# -*- coding: utf-8 -*-
from authenticate.utils import serialize_object
from authenticate.database import Column, Model, SurrogatePK, db, reference_col, relationship
import datetime as dt


class Category(SurrogatePK, Model):
    """A category for scopes."""

    __tablename__ = 'categories'
    name = Column(db.String(80), unique=True, nullable=False)
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
        return '<Category({name})>'.format(name=self.name)