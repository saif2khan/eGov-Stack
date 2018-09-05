# -*- coding: utf-8 -*-
from authenticate.database import Column, Model, SurrogatePK, db, reference_col, relationship


class InvalidToken(SurrogatePK, Model):
    """A category for scopes."""

    __tablename__ = 'invalid_tokens'
    token = Column(db.String(255), unique=True, nullable=False)

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<InvalidToken({name})>'.format(name=self.token)