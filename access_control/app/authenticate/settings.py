# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    """This secret key should be changed with each installation of this app. It should be set up as an environment variable and the 'secret-key' is just a placeholder in case an environment variable is not set."""
    SECRET_KEY = os.environ.get('AUTHENTICATE_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_PHONE_REGION = 'US'
    APPROVED_ROLES = ['READ', 'READ-WRITE', 'ADMIN']
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = os.environ.get('MAIL_PORT', 25)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'user')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'secret-key') # please use env variable
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', False)
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', False)

class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None) 


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None) or \
        'sqlite:///' + os.path.join(Config.APP_DIR, DB_NAME)


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    DB_NAME = 'test.db'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None) or \
        'sqlite:///' + os.path.join(Config.APP_DIR, DB_NAME)
    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
