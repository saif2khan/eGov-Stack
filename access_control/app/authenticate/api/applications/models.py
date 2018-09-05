# -*- coding: utf-8 -*-
from authenticate.utils import serialize_object
from authenticate.database import Column, Model, SurrogatePK, db, reference_col, relationship
import datetime as dt
import json


class Application(SurrogatePK, Model):
    """A category for scopes."""

    __tablename__ = 'applications'
    name = Column(db.String(80), unique=True, nullable=False)
    _white_listed_ips = Column(db.Text, default="[]")
    created_on = Column(db.DateTime, default=dt.datetime.now())
    last_update = Column(db.DateTime, onupdate=dt.datetime.now())

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    @property
    def white_listed_ips(self):
        return json.loads(self._white_listed_ips)

    @white_listed_ips.setter
    def white_listed_ips(self, value):
        self._white_listed_ips = json.dumps(json.loads(value))    

    @property
    def serialized(self):
        print(self.white_listed_ips, type(self.white_listed_ips))
        return serialize_object(self, self.__class__, white_listed_ips=self.white_listed_ips)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Application({name})>'.format(name=self.name)