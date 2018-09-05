# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""

from authenticate.settings import DevConfig, ProdConfig
from authenticate.extensions import mail
from flask_mail import Message
from threading import Thread
import requests

CONFIG = ProdConfig


def send_async_email(msg, app):
    with app.app_context():
        mail.send(msg)

def send_email(sender, subject, to, text):
    """Send through mailgun if an API key exists, otherwise
    attempt to send use the flask_mail extension which depends
    on the correct SMTP settings to be input in the settings.py file"""
    if CONFIG.MAILGUN_API_KEY:
        return requests.post(
        "https://api.mailgun.net/v3/{}/messages".format(CONFIG.MAILGUN_DOMAIN),
        auth=("api", CONFIG.MAILGUN_API_KEY),
        data={"from": sender,
              "to": to,
              "bcc": [],
              "subject": subject,
              "text": text})
    from authenticate.app import create_app
    msg = Message(subject, sender=sender, recipients=to)
    msg.body = text
    app = create_app(CONFIG)
    thr = Thread(target=send_async_email, args=[msg, app])
    thr.start()

