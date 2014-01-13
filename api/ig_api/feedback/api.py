# -*- coding: utf-8 -*-
import datetime

from flask import g
from flask.ext.restful import Resource, reqparse, fields, marshal_with
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

from ig_api import api, db
from ig_api.error_codes import abort_error
from ig_api.authentication import login_required
from ig_api.feedback.models import (FormModel, InstanceModel, FormException, InstanceException,
        FormFieldSubModel, FeedbackModel, FeedbackException)


## Helpers
def form_id_exists(form_id):
    """Checks for the existence of the form with the given form ID or
    aborts the request with the code '4001'. Incase the form exists,
    it returns the form object.

    Note: This will be used by API endpoints to check the existence of
          a form.
    """
    try:
        form = FormModel.objects.get(id=ObjectId(form_id))
    except (db.ValidationError, InvalidId, db.DoesNotExist):
        abort_error(4001)

    return form


def instance_id_exists(instance_id):
    """Does the same for instance id what `form_id_exists` does for form ID.
    Code of error raised: 4003
    """

    try:
        instance = InstanceModel.objects.get(id=ObjectId(instance_id))
    except (db.ValidationError, InvalidId, db.DoesNotExist):
        abort_error(4003)

    return instance


## Custom flask-restful field for response objects in the field
class FeedbackResponseField(fields.Raw):
    """There is a need to write this class as `FeedbackModel` is treated as
    an indexable object and a key lookup is done by flask-restful's normal
    process but the `responses` is an attribute of the `FeedbackModel`
    """
    def output(self, key, obj):
        value = obj.responses

        return self.format(value)

## Different objects to be returns (to be used with `marshal_with`)
merchant_obj = {
    'id': fields.String,
    'name': fields.String,
    'address': fields.String,
    'contact_number': fields.String,
    'current_balance': fields.Float,
    'logo': fields.String
}

field_obj = {
    'id': fields.String,
    'type': fields.String(attribute='field_type'),
    'text': fields.String,
    'choices': fields.List(fields.String)
}

form_obj = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'fields': fields.List(fields.Nested(field_obj)),
    'merchant': fields.Nested(merchant_obj),
    'customer_details_heading': fields.String,
    'feedback_heading': fields.String,
    'nps_score_heading': fields.String
}

instance_obj = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'location': fields.String
}

customer_obj = {
    'id': fields.String,
    'name': fields.String,
    'mobile': fields.String,
    'email': fields.String
}

feedback_obj = {
    'id': fields.String,
    'received_at': fields.DateTime,
    'customer': fields.Nested(customer_obj),
    'instance': fields.Nested(instance_obj, attribute='form_instance'),
    'form': fields.Nested(form_obj, attribute='form_instance.form'),
    'nps_score': fields.Integer,
    'feedback_text': fields.String,
    'responses': FeedbackResponseField
}

analytics_obj = {
    'numbers': fields.Raw,
    'field': fields.Nested(field_obj)
}

## Endpoints


class FormList(Resource):

    # to parse the JSON about the fields of the feedback form
    def form_fields(fields):
        # if all the fields are not provided in the form of a list
        if not type(fields) is list:
            raise ValueError("Fields should be provided within a list.")

        # this list will have all the `FormFieldSubModel` instances of the fields provided
        form_fields = []
        for field in fields:
            # if the field is not of type dictionary
            if not type(field) is dict:
                raise ValueError("Every field should comprise of a dictionary.")
            # this will ensure that the field has the correct kind of keys
            form_field = FormFieldSubModel(field_type=field.get('type'), text=field.get('text'), choices=field.get('choices')) 
            try:
                form_field.validate()
            except db.ValidationError:
                raise ValueError("There is some problem with the fields provided.")
            form_fields.append(form_field)
        
        return form_fields

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', required=True, type=unicode, location='json')
    post_parser.add_argument('description', required=True, type=unicode, location='json')
    post_parser.add_argument('feedback_heading', required=True, type=unicode, location='json')
    post_parser.add_argument('nps_score_heading', required=True, type=unicode, location='json')
    post_parser.add_argument('customer_details_heading', required=True, type=unicode, location='json')
    post_parser.add_argument('fields', required=True, type=form_fields, location='json')
    get_fields = {
        'error': fields.Boolean(default=False),
        'forms': fields.List(fields.Nested(form_obj))
    }

    post_fields = {
        'error': fields.Boolean(default=False),
        'form': fields.Nested(form_obj)
    }

    @login_required('merchant')
    @marshal_with(get_fields)
    def get(self):
        #TODO: add pagination support.
        forms = FormModel.objects.filter(merchant=g.user.merchant)

        return {'forms': forms}

    @login_required('merchant')
    @marshal_with(post_fields)
    def post(self):
        args = self.post_parser.parse_args()

        # create form
        try:
            form = FormModel.create(merchant=g.user.merchant, **args)
        except FormException:
            abort_error(4000)

        return {'form': form}


class Form(Resource):

    get_fields = {
        'error': fields.Boolean(default=False),
        'form': fields.Nested(form_obj)
    }

    @login_required('merchant')
    @marshal_with(get_fields)
    def get(self, form_id):
        form = form_id_exists(form_id)

        return {'form': form}


class FormInstanceList(Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', required=True, type=unicode, location='json')
    post_parser.add_argument('description', required=True, type=unicode, location='json')
    post_parser.add_argument('location', required=True, type=unicode, location='json')

    post_fields = {
        'error': fields.Boolean(default=False),
        'instance': fields.Nested(instance_obj)
    }
    
    get_fields = {
        'error': fields.Boolean(default=False),
        'instances': fields.List(fields.Nested(instance_obj)),
    }

    @login_required('merchant')
    @marshal_with(get_fields)
    def get(self, form_id):
        form = form_id_exists(form_id)

        instances = InstanceModel.objects.filter(form=form)

        return {'instances': instances}

    @login_required('merchant')
    @marshal_with(post_fields)
    def post(self, form_id):
        form = form_id_exists(form_id)
        args = self.post_parser.parse_args()

        # create instance
        try:
            instance = form.create_instance(**args)
        except InstanceException:
            abort_error(4002)
        
        return {'instance': instance}


class FormInstance(Resource):

    get_fields = {
        'error': fields.Boolean(default=False),
        'instance': fields.Nested(instance_obj)
    }

    @login_required('merchant')
    @marshal_with(get_fields)
    def get(self, form_id, instance_id):
        form = form_id_exists(form_id)
        instance = instance_id_exists(instance_id)

        return {'instance': instance}


class CustomerFeedback(Resource):

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('nps_score', required=True, type=unicode, location='json')
    put_parser.add_argument('feedback_text', required=True, type=unicode, location='json')
    put_parser.add_argument('field_responses', required=True, type=dict, location='json')
    put_parser.add_argument('customer_name', required=False, type=unicode, location='json')
    put_parser.add_argument('customer_mobile', required=False, type=unicode, location='json')
    put_parser.add_argument('customer_email', required=False, type=unicode, location='json')
    
    get_fields = {
        'error': fields.Boolean(default=False),
        'form': fields.Nested(form_obj)        
    }

    put_fields = {
        'error': fields.Boolean(default=False),
        'success': fields.Boolean
    }

    @marshal_with(get_fields)
    def get(self, instance_id):
        instance = instance_id_exists(instance_id)
        form = instance.form

        return {'form': form}

    @marshal_with(put_fields)
    def put(self, instance_id):
        args = self.put_parser.parse_args()
        instance = instance_id_exists(instance_id)

        customer_details = None
        if args.get('customer_name') or args.get('customer_mobile') or args.get('customer_email'):
            customer_details = {
                'name': args.get('customer_name'),
                'mobile': args.get('customer_mobile'),
                'email': args.get('customer_email')
            }
        
        # save customer feedback
        try:
            FeedbackModel.create(args['nps_score'], args['feedback_text'], args['field_responses'], instance, customer_details)
        except FeedbackException:
            abort_error(4004)

        return {'success': True}


class FeedbackTimeline(Resource):

    get_fields = {
        'error': fields.Boolean(default=False),
        'feedbacks': fields.List(fields.Nested(feedback_obj))
    }

    def nps_score_type(value, key):
        try:
            value = int(value)
        except ValueError:
            raise ValueError("'{0}' should be of int type.").format(key)

        # nps score should be in the range of 1 to 10
        if value < 1 or value > 10:
            raise ValueError("'{0}' should be between 1 and 10.").format(key)

        return value

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('nps_score_start', required=False, type=nps_score_type, location='args')
    get_parser.add_argument('nps_score_end', required=False, type=nps_score_type, location='args')

    @marshal_with(get_fields)
    @login_required('merchant')
    def get(self):
        merchant = g.user.merchant
        args = self.get_parser.parse_args()
        print args
        if args['nps_score_start'] and args['nps_score_end']:
            print 'this is good'
            feedbacks = FeedbackModel.objects.filter(merchant=merchant, nps_score__gte=args['nps_score_start'], 
                    nps_score__lte=args['nps_score_end']).order_by("-received_at")
        else:
            feedbacks = FeedbackModel.objects.filter(merchant=merchant).order_by("-received_at")

        return {'feedbacks': feedbacks}


class FeedbackAnalytics(Resource):

    def date_arg(value, key):
        try:
            year, month, day = value.split('-')
            if key == 'end_date':
                date = datetime.datetime(int(year), int(month), int(day), hour=23, minute=59, second=59)
            else: # if key == 'start_date'
                date = datetime.datetime(int(year), int(month), int(day), hour=0, minute=0, second=0)
        except ValueError:
            raise ValueError("There was some problem with the date provided.")

        return date

    get_fields = {
        'error': fields.Boolean(default=False),
        'analytics': fields.List(fields.Nested(analytics_obj))
    }

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('instance_ids', required=True, type=unicode, location='args')
    get_parser.add_argument('start_date', required=False, type=date_arg, location='args')
    get_parser.add_argument('end_date', required=False, type=date_arg, location='args')

    @marshal_with(get_fields)
    @login_required('merchant')
    def get(self, form_id):
        form = form_id_exists(form_id)
        args = self.get_parser.parse_args()

        # check if all the given instances exist
        instance_ids = args['instance_ids'].split(',')
        instances = []
        for id in instance_ids:
            instance = instance_id_exists(id)
            instances.append(instance)

        if args['start_date'] and args['end_date']:
            analytics = form.get_analytics(instances, args['start_date'], args['end_date'])
        else:
            analytics = form.get_analytics(instances)

        return {'analytics': [v for k,v in analytics.items()]}

## Registering Endpoints

# merchant dashboard
api.add_resource(FormList, '/dashboard/forms')
api.add_resource(Form, '/dashboard/forms/<form_id>')
api.add_resource(FormInstanceList, '/dashboard/forms/<form_id>/instances')
api.add_resource(FormInstance, '/dashboard/forms/<form_id>/instances/<instance_id>')
api.add_resource(FeedbackTimeline, '/dashboard/timeline')
api.add_resource(FeedbackAnalytics, '/dashboard/forms/<form_id>/analytics')

# customer facing
api.add_resource(CustomerFeedback, '/customer/feedback/<instance_id>')
