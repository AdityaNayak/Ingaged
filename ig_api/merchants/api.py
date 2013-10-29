# -*- coding: utf-8 -*-
from cStringIO import StringIO

from flask.ext.restful import Resource, reqparse, fields, marshal_with
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from werkzeug.datastructures import FileStorage
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

from ig_api import api, db, app
from ig_api.error_codes import abort_error
from ig_api.authentication import login_required
from ig_api.merchants.models import MerchantModel

__all__ = ['MerchantList', 'Merchant', 'MerchantUploadLogo']


## Helpers
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

def upload_s3(file, key_name, content_type, bucket_name):
    """Uploads a given StringIO object to S3. Closes the file after upload.

    Returns the URL for the image.

    Note: The acl for the file is set as 'public-acl' for the file uploaded.

    Keyword Arguments:
    file -- StringIO object which needs to be uploaded.
    key_name -- key name to be kept in S3.
    content_type -- content type that needs to be set for the S3 object.
    bucket_name -- name of the bucket where file needs to be uploaded.
    """
    # create connection
    conn = S3Connection(app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY'])

    # upload the file after getting the right bucket
    bucket = conn.get_bucket(bucket_name)
    obj = S3Key(bucket)
    obj.name = key_name
    obj.content_type = content_type
    obj.set_contents_from_string(file.getvalue())
    obj.set_acl('public-read')

    # close stringio object
    file.close()

    return obj.generate_url(expires_in=0, query_auth=False)

def logo_s3_setup():
    """This simple helper function creates a new bucket for the logos
    and uploads the default logo to that bucket.

    Note: This method would be used while deploying code and it would ensure
          that the required bucket is created with the default logo. So
          basically before beginning with any uploads this methods needs to be run.
    """
    # create connection
    conn = S3Connection(app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY'])

    # create logos bucket
    bucket = conn.create_bucket(app.config['AWS_S3_LOGO_BUCKET'])

    # upload default logo
    default_logo_obj = S3Key(bucket)
    default_logo_obj.name = app.config['AWS_S3_DEFAULT_LOGO_KEY_NAME']
    default_logo_obj.set_contents_from_filename(app.config['AWS_S3_DEFAULT_LOGO_FILE'])
    default_logo_obj.set_acl('public-read')

def merchant_id_exists(merchant_id):
    """Checks for the existence of given merchant ID or aborts the request
    with the code '2003' or returns the `MerchantModel` object.

    Note: This will be used in API endpoints to check for the existence of
          the merchant.
    """
    # check for existence of merchant with given merchant_id 
    try:
        merchant = MerchantModel.objects.get(id=ObjectId(merchant_id))
    except (db.ValidationError, InvalidId, db.DoesNotExist):
        abort_error(2003)

    return merchant

## Different objects to be returned (to be used with `marshal_with`)

merchant_obj = {
    'id': fields.String,
    'name': fields.String,
    'address': fields.String,
    'contact_number': fields.String,
    'logo': fields.String
}


## Endpoints

class MerchantList(Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', required=True, type=unicode, location='json')
    post_parser.add_argument('address', required=True, type=unicode, location='json')
    post_parser.add_argument('contact_number', required=False, type=unicode, location='json')

    post_fields = {
        'error': fields.Boolean(default=False),
        'merchant': fields.Nested(merchant_obj)
    }

    get_fields = {
        'error': fields.Boolean(default=False),
        'merchants': fields.List(fields.Nested(merchant_obj))
    }

    @login_required('admin')
    @marshal_with(post_fields)
    def post(self):
        args = self.post_parser.parse_args()

        # create merchant
        try:
            merchant = MerchantModel.create_merchant(**args)
        except db.ValidationError: # incorrect data provided by user
            abort_error(2000)

        return {'merchant': merchant}

    @login_required('admin')
    @marshal_with(get_fields)
    def get(self):
        #TODO: add pagination support
        merchants = MerchantModel.objects.all()

        return {'merchants': merchants}


class MerchantUploadLogo(Resource):

    put_parser = reqparse.RequestParser(argument_class=FileStorageArgument)
    put_parser.add_argument('logo', required=True, type=FileStorage, location='files')

    put_fields = {
        'error': fields.Boolean(default=False),
        'logo_url': fields.String
    }

    @login_required('admin')
    @marshal_with(put_fields)
    def put(self, merchant_id):
        #TODO: a check on file size needs to be there.
        merchant = merchant_id_exists(merchant_id)

        args = self.put_parser.parse_args()
        logo = args['logo']

        # check logo extension
        extension = logo.filename.rsplit('.', 1)[1].lower()
        if '.' in logo.filename and not extension in app.config['LOGO_ALLOWED_EXTENSIONS']:
            abort_error(2001)

        # create a file object of the logo
        logo_file = StringIO()
        logo.save(logo_file)

        # upload to s3
        key_name = '{0}.{1}'.format(merchant_id, extension)
        content_type = app.config['IMAGE_CONTENT_TYPES'][extension]
        bucket_name = app.config['AWS_S3_LOGO_BUCKET']
        logo_url = upload_s3(logo_file, key_name, content_type, bucket_name)
        
        # change the merchant's logo url
        merchant.logo = logo_url
        merchant.save()

        return {'logo_url': merchant.logo}

class Merchant(Resource):

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('name', required=True, type=unicode, location='json')
    put_parser.add_argument('address', required=True, type=unicode, location='json')
    put_parser.add_argument('contact_number', required=False, type=unicode, location='json')

    get_fields = {
        'error': fields.Boolean(default=False),
        'merchant': fields.Nested(merchant_obj)
    }

    put_fields = {
        'error': fields.Boolean(default=False),
        'merchant': fields.Nested(merchant_obj)
    }

    @login_required('admin')
    @marshal_with(get_fields)
    def get(self, merchant_id):
        merchant = merchant_id_exists(merchant_id)

        return {'merchant': merchant}


    @login_required('admin')
    @marshal_with(put_fields)
    def put(self, merchant_id):
        merchant = merchant_id_exists(merchant_id)
        args = self.put_parser.parse_args()

        # update merchant object attributes and save
        for arg,value in args.items():
            setattr(merchant, arg, value)
        
        # because contact number might exist before
        # and has been deleted in the edit operation
        if not args.get('contact_number'):
            merchant.contact_number = None #TODO: find a better way to do this.

        merchant.save()

        return {'merchant': merchant}


## Registering Endpoints

# admin panel
api.add_resource(MerchantList, '/admin/merchants')
api.add_resource(Merchant, '/admin/merchants/<merchant_id>')
api.add_resource(MerchantUploadLogo, '/admin/merchants/<merchant_id>/upload_logo')
