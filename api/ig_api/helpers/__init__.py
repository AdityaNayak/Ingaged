# -*- coding: utf-8 -*-
import datetime

from flask import render_template
from flask.ext.restful import reqparse, fields
from werkzeug.datastructures import FileStorage
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key


from ig_api import app
from ig_api.aws import SESMessage

## S3 Upload
def upload_s3(file, key_name, content_type, bucket_name, headers={}):
    """Uploads a given StringIO object to S3. Closes the file after upload.

    Returns the URL for the image.

    Note: The acl for the file is set as 'public-acl' for the file uploaded.

    Keyword Arguments:
    file -- StringIO object which needs to be uploaded.
    key_name -- key name to be kept in S3.
    content_type -- content type that needs to be set for the S3 object.
    bucket_name -- name of the bucket where file needs to be uploaded.
    headers -- (optional) dict of headers which need to be set for the uploaded file.
    """
    # create connection
    conn = S3Connection(app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY'])

    # upload the file after getting the right bucket
    bucket = conn.get_bucket(bucket_name)
    obj = S3Key(bucket)
    obj.name = key_name
    obj.content_type = content_type
    obj.set_contents_from_string(file.getvalue(), headers=headers)
    obj.set_acl('public-read')

    # close stringio object
    file.close()

    return obj.generate_url(expires_in=0, query_auth=False)

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
