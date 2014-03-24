# -*- coding: utf-8 -*-
import datetime
from cStringIO import StringIO

from flask.ext.restful import Resource, reqparse, fields, marshal_with
from flask.ext.restful.fields import MarshallingException
from boto.s3.connection import S3Connection
from boto.s3.key import Key as S3Key
from werkzeug.datastructures import FileStorage
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

from ig_api import api, db, app
from ig_api.error_codes import abort_error
from ig_api.helpers import FileStorageArgument, DateTimeFieldType, DateTimeField, upload_s3
from ig_api.authentication import login_required
from ig_api.authentication.models import MerchantUserException
from ig_api.merchants.models import MerchantModel, PaymentModel, MerchantException

__all__ = ['MerchantList', 'Merchant', 'MerchantUploadLogo']


## Helpers
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

    # merchant details
    'id': fields.String,
    'name': fields.String,
    'address': fields.String,
    'contact_number': fields.String,
    'current_balance': fields.Float,
    'logo': fields.String,

    # nps notification details
    'nps_notifs': fields.Boolean,
    'nps_threshold': fields.Integer,
    'notif_emails': fields.List(fields.String)

}

payment_obj = {
    'id': fields.String,
    'amount': fields.Float,
    'notes': fields.String,
    'received_at': DateTimeField,
    'key_in_at': DateTimeField
}

## Endpoints

class MerchantList(Resource):

    post_parser = reqparse.RequestParser()
    # merchant details
    post_parser.add_argument('name', required=True, type=unicode, location='json')
    post_parser.add_argument('address', required=True, type=unicode, location='json')
    post_parser.add_argument('contact_number', required=False, type=unicode, location='json')
    # merchant user details
    post_parser.add_argument('user_name', required=True, type=unicode, location='json') # name of the user
    post_parser.add_argument('user_username', required=True, type=unicode, location='json') # this is the username
    post_parser.add_argument('user_email', required=True, type=unicode, location='json')
    post_parser.add_argument('user_password', required=True, type=unicode, location='json')

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

        # merchant user details
        user_details = {
            'name': args.pop('user_name'),
            'username': args.pop('user_username'),
            'email': args.pop('user_email'),
            'password': args.pop('user_password')
        }

        # create merchant
        try:
            merchant = MerchantModel.create_merchant(user_details=user_details, **args)
        except MerchantException:
            abort_error(2000)
        except MerchantUserException:
            abort_error(3000)

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

    def emails_arg(value, key):
        """Expects a comma seperated strings of emails and validates them.
        Returns a list of e-Mails.
        """

        # check if value of str or unicode type
        if type(value) is not unicode:
            raise ValueError("There was some problem with the e-Mail(s) provided.")

        # split emails into a list
        emails = value.split(',')

        # check if all emails are being validated
        for email in emails:
            try:
                db.EmailField().validate(email)
            except db.ValidationError:
                raise ValueError("There was some problem with the e-Mail(s) provided.")

        return emails

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('name', required=True, type=unicode, location='json')
    put_parser.add_argument('address', required=True, type=unicode, location='json')
    put_parser.add_argument('contact_number', required=False, type=unicode, location='json')
    # nps score related notification details
    put_parser.add_argument('nps_notifs', required=True, type=bool, location='json')
    put_parser.add_argument('notif_emails', required=False, type=emails_arg, location='json')
    put_parser.add_argument('nps_threshold', required=False, type=int, location='json', choices=range(1, 11))

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

        # add nps based notification details if provided
        if args['nps_notifs'] is True:
            # abort if other details are provided correctly
            if not args.get('notif_emails') and not args.get('nps_threshold'):
                abort_error(2000)
            # continue if all the details are provided
            merchant.nps_notifs = args['nps_notifs']
            merchant.notif_emails = args.pop('notif_emails')
            merchant.nps_threshold = args.pop('nps_threshold')
        # remove all nps details if nps_notifs is False
        else:
            merchant.nps_notifs = False
            merchant.notif_emails = None
            merchant.nps_threshold = None

        # update merchant object attributes and save
        for arg,value in args.items():
            setattr(merchant, arg, value)
        
        # because contact number might exist before
        # and has been deleted in the edit operation
        if not args.get('contact_number'):
            merchant.contact_number = None #TODO: find a better way to do this.

        merchant.save()

        return {'merchant': merchant}


class MerchantPaymentsList(Resource):

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('amount', required=True, type=float, location='json')
    put_parser.add_argument('method', required=True, type=int, choices=[i[0] for i in PaymentModel.METHOD_CHOICES], location='json')
    put_parser.add_argument('notes', required=False, type=unicode, location='json')
    put_parser.add_argument('received_at', required=True, type=DateTimeFieldType, location='json')

    get_fields = {
        'error': fields.Boolean(default=False),
        'payments': fields.List(fields.Nested(payment_obj)),
    }

    post_fields = {
        'error': fields.Boolean(default=False),
        'payment': fields.Nested(payment_obj),
    }

    @login_required('admin')
    @marshal_with(post_fields)
    def post(self, merchant_id):
        merchant = merchant_id_exists(merchant_id)
        args = self.put_parser.parse_args()

        # check the receive date time is less than current date and time
        if args['received_at'] > datetime.datetime.utcnow():
            print 'this is bullshit'
            abort_error(2004)

        # create new payment
        try:
            payment = PaymentModel.key_in(merchant=merchant, **args)
        except db.ValidationError:
            abort_error(2004)

        return {'payment': payment}

    @login_required('admin')
    @marshal_with(get_fields)
    def get(self, merchant_id):
        #TODO: add pagination support
        merchant = merchant_id_exists(merchant_id)

        # get payment objects of the merchant
        payments = PaymentModel.objects.filter(merchant=merchant)

        return {'payments': payments}


## Registering Endpoints

# admin panel
api.add_resource(MerchantList, '/admin/merchants')
api.add_resource(Merchant, '/admin/merchants/<merchant_id>')
api.add_resource(MerchantUploadLogo, '/admin/merchants/<merchant_id>/upload_logo')
api.add_resource(MerchantPaymentsList, '/admin/merchants/<merchant_id>/payments')
