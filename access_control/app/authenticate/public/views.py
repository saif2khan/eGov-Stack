from flask import Blueprint, render_template, flash, redirect, url_for, request, session, abort
from authenticate.settings import Config
from authenticate.api.user.models import User
from authenticate.extensions import db
from itsdangerous import URLSafeTimedSerializer as Serializer
import datetime

blueprint = Blueprint('public', __name__, url_prefix='/public')

@blueprint.route('/forgot-password', methods=['GET', 'POST'])
@blueprint.route('/forgot-password/<token>', methods=['GET', 'POST'])
def forgot_password(token=None):
    if token:
        s = Serializer(Config.SECRET_KEY)
        try:
            email = s.loads(token, salt="recover-key", max_age=3600)
        except:
            abort(404)
        if request.method == 'POST':
            user = User.query.filter_by(email=email).first()
            if user:
                user.set_password(request.form.get('password').encode('utf-8'))
                user.save()
                return render_template('forgot-password.html', token=token, result='Password Updated')
        else:
            return render_template('forgot-password.html', token=token)
    else:
        return render_template('forgot-password.html', token=token)