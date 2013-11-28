# -*- coding: utf-8 -*-
import datetime

from flask import render_template
from flask.ext.restful import reqparse, fields
from werkzeug.datastructures import FileStorage

from ig_api import app
from ig_api.aws import SESMessage

## Flask-Restful


class FileStorageArgument(reqparse.Argument):
    """This argument class for flask-restful will be used in
    all cases where file uploads need to be handled."""
    
    def convert(self, value, op):
        if self.type is FileStorage:  # only in the case of files
            # this is done as self.type(value) makes the name attribute of the
            # FileStorage object same as argument name and value is a FileStorage
            # object itself anyways
            return value

        # called so that this argument class will also be useful in
        # cases when argument type is not a file.
        super(FileStorageArgument, self).convert(*args, **kwargs)


class DateTimeField(fields.Raw):
    """Formats the DateTime object in the ISO8016 format for JSON."""

    def format(self, value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        raise MarshallingException("Only DateTime objects can be marshalled.")


def DateTimeFieldType(value):
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')


## SES e-Mails


def send_trans_email(trans_name, name, email, template_vars={}):
    """Sends a transactional email.

    Keyword Arguments:
    trans_name -- a key name in the dict `app.config['TRANSACTIONAL_EMAILS']`
    name -- name of the user
    email -- email of the user
    template_vars -- variables using which template of the email needs to be rendered
    """
    email_details = app.config['TRANSACTIONAL_EMAILS'][trans_name]
    msg = SESMessage(email_details['from'], '{0} <{1}>'.format(name, email), email_details['subject'])
    msg.html = render_template(email_details['template'], **template_vars)
    msg.send()
