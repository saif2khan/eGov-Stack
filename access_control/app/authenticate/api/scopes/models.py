# -*- coding: utf-8 -*-
from authenticate.utils import serialize_object
from authenticate.database import Column, Model, SurrogatePK, db, reference_col, relationship
import datetime as dt


class Scope(SurrogatePK, Model):
    """A scope which is hierarchical model."""

    __tablename__ = 'scopes'
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(80), nullable=False)
    parent_scope_id = Column(db.Integer, db.ForeignKey('scopes.id'))
    created_on = Column(db.DateTime, default=dt.datetime.now())
    last_update = Column(db.DateTime, onupdate=dt.datetime.now())
    parent = relationship('Scope', lazy="joined", join_depth=8, backref='children', remote_side=id)
    category_id = reference_col('categories', nullable=True)
    category = relationship('Category', backref='scopes')

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    @property
    def serialized(self):
        return serialize_object(self, self.__class__)

    def tree_serialized(self, user):
        return serialize_object(self, self.__class__,
                                children=[
                                    child.tree_serialized(user) \
                                    if user.can.view.scope_id(self.id) \
                                    else {'id': self.id, 'error': 'not authorized'} \
                                    for child in self.children])

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Scope({name}:{id})>'.format(name=self.name, id=self.id)