# -*- coding: utf-8 -*-
from authenticate.utils import serialize_object
from authenticate.database import Column, Model, SurrogatePK, db, reference_col, relationship
import datetime as dt
import json
from authenticate.settings import Config
from itsdangerous import URLSafeSerializer as Serializer

s = Serializer(Config.SECRET_KEY)


class AppContext(SurrogatePK, Model):
    """A context for an APP"""

    __tablename__ = 'app_contexts'
    name = Column(db.String(80), unique=True, nullable=False)
    _context_credentials = Column(db.Text, nullable=False)
    application_id = reference_col('applications', nullable=True)
    application = relationship('Application', backref='app_contexts')
    created_on = Column(db.DateTime, default=dt.datetime.now())
    last_update = Column(db.DateTime, onupdate=dt.datetime.now())
    is_active = Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    @property
    def context_credentials(self):
        return json.loads(s.loads(self._context_credentials))

    @context_credentials.setter
    def context_credentials(self, value):
        self._context_credentials = s.dumps(json.dumps(json.loads(value)))

    @property
    def serialized(self):
        return serialize_object(self, self.__class__, context_credentials=self.context_credentials)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<AppContext({name})>'.format(name=self.name)