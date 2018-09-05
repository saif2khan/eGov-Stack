# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import datetime as dt
from flask import g, request
import dateutil.parser
from datetime import *
from validate_email import validate_email
from authenticate.settings import DevConfig, ProdConfig
from authenticate.extensions import mail

CONFIG = ProdConfig

def abort(error_code):
    msg_dict = {
        401: 'Unable to authenticate request'
    }
    return {
        'message': msg_dict.get(error_code, 'There was a problem with your request.'),
        'is_successful': False
    }, error_code

def try_parsing_date(text):
    if not text or text == 'Invalid date':
        return None
    for fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%-m/%-d/%Y', '%m/%d/%Y', '%m/%d/%Y, %I:%M %p'):
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            return dateutil.parser.parse(text) + timedelta(seconds=time.localtime().tm_gmtoff)
    raise ValueError('no valid date format found')


def serialize_object(inst, cls, **kwargs):
    serialized = {}
    for name, value in kwargs.items():
        try:
            serialized[name] = [x.serialized if x else None for x in value]
        except (AttributeError, TypeError) as e:
            # print(e, 'BAD ERROR')
            try:
                serialized[name] = value
            except Exception as e:
                print(e)
                pass
    for column in cls.__table__.columns:
        attribute = getattr(inst, column.name)
        if column.name[0] == '_':
            pass
        elif isinstance(attribute, dt.datetime):
            serialized[column.name] = attribute.isoformat()
        elif isinstance(attribute, dt.date):
            serialized[column.name] = attribute.strftime('%m/%d/%Y')
        elif repr(attribute)[0:7] == 'Decimal':
            serialized[column.name] = float(attribute)
        elif isinstance(attribute, (bytes, bytearray)):
            pass
        else:
            try:
                serialized[column.name] = attribute
            except:
                serialized[column.name] = str(repr(attribute))
    return serialized