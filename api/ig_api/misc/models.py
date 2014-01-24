# -*- coding: utf-8 -*-

from ig_api import db, app
from ig_api.helpers import send_trans_email


## Exceptions

class SignUpRequestException(Exception):
    def __init__(self):
        self.message = 'There was a problem while saving the sign up request.'


## Models

class SignUpRequestModel(db.Document):
    name = db.StringField(required=True)
    email = db.EmailField(required=True)
    phone = db.StringField()

    meta = {'collection': 'signup_requests'}

    @staticmethod
    def create(name, email, phone=None):
        """Creates a new model with the details of the sign up request."""
        # create model
        request = SignUpRequestModel(name=name, email=email)
        if phone:
            request.phone = phone
        # raise error in case of validation problem
        try:
            request.save()
        except (db.ValidationError):
            raise SignUpRequestException

        # send e-Mail
        email_vars = {
            'name': name,
            'email': email,
            'phone': phone
        }
        send_trans_email('signup_request', 'InGage Admin', app.config['ADMIN_EMAIL'], email_vars)

        return request

    def __repr__(self):
        return '<SignUpRequestModel: {0}, {1}>'.format(self.name, self.email)
