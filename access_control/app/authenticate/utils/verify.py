# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
from authenticate.extensions import auth
from authenticate.api.auth.models import InvalidToken
from flask import g, request

@auth.verify_password
def verify(username_or_token=None, password=None):
    from authenticate.api.user.models import User
    from authenticate.api.applications.models import Application
    from authenticate.api.user.models import User

    """Checks if the request is coming from an application that is IP Whitelisted."""
    if request.headers.get('X-Application-Name', None):
        application = Application.query.filter_by(name=request.headers.get('X-Application-Name')).first()

        if application and request.headers.get('X-Forwarded-For', request.remote_addr) in application.white_listed_ips:
            g.user = User(app_user=True) 
            return True

    # check if token has been invalidated
    invalid_token = InvalidToken.query.filter_by(token=username_or_token).first()
    if invalid_token:
        return False

    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)

    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()

        # Deleted users shouldn't authenticate
        if user and user.is_deleted:
            return False

        # Exception for posting to the users endpoint for initial user creation
        if request.endpoint == 'userapi' and request.method == 'POST':
            g.user = user
            return True

        if not user or not user.check_password(password):
            return False
    g.user = user
    g.token = username_or_token
    return True