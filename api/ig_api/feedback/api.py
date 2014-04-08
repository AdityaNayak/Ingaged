# -*- coding: utf-8 -*-
import datetime, math, csv, StringIO

from flask import g
from flask.ext.restful import Resource, reqparse, fields, marshal_with
from flask.ext.restful.fields import get_value
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

from ig_api import api, db
from ig_api.error_codes import abort_error
from ig_api.helpers import upload_s3
from ig_api.authentication import login_required
from ig_api.feedback.models import (FormModel, InstanceModel, FormException, InstanceException,
        FormFieldSubModel, FeedbackModel, FeedbackException)


## Helpers
def nps_score_type(value, key):
    try:
        value = int(value)
    except ValueError:
        raise ValueError("'{0}' should be of int type.").format(key)

    # nps score should be in the range of 1 to 10
    if value < 1 or value > 10:
        raise ValueError("'{0}' should be between 1 and 10.").format(key)

    return value

def date_arg(value, key):
    """This is the date argument for Flask-Restful.
    
    Processes the date given in 'YYYY-MM-DD' format and returns a `datetime.datetime`
    object from it.
    """
    try:
        year, month, day = value.split('-')
        if key == 'end_date':
            date = datetime.datetime(int(year), int(month), int(day), hour=23, minute=59, second=59)
        else: # if key == 'start_date'
            date = datetime.datetime(int(year), int(month), int(day), hour=0, minute=0, second=0)
    except ValueError:
        raise ValueError("There was some problem with the date provided.")

    return date

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

field_obj = {
    'id': fields.String,
    'type': fields.String(attribute='field_type'),
    'required': fields.Boolean,
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
    'nps_score_heading': fields.String,
    'incremental_id': fields.Boolean,
    'css_class_name': fields.String,
    'display_card_html': fields.String
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

    # unique feedback ID
    'id': fields.String,
    
    # form & instance objects
    'instance': fields.Nested(instance_obj, attribute='form_instance'),
    'form': fields.Nested(form_obj, attribute='form_instance.form'),

    # feedback information
    'nps_score': fields.Integer,
    'feedback_text': fields.String,
    'received_at': fields.DateTime,
    'customer': fields.Nested(customer_obj),
    'responses': FeedbackResponseField,

    # counter infromation (for forms which generate a feedback ID)
    'has_counter': fields.Boolean,
    'counter': fields.Integer,

}

analytics_obj = {
    'numbers': fields.Raw,
    'total_responses': fields.Integer,
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
            form_field = FormFieldSubModel(field_type=field.get('type'), text=field.get('text'),
                    choices=field.get('choices'), required=field.get('required'))
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
    post_parser.add_argument('incremental_id', required=True, type=bool, location='json')
    post_parser.add_argument('css_class_name', required=True, type=unicode, location='json')
    post_parser.add_argument('display_card_html', required=True, type=unicode, location='json')
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
    put_parser.add_argument('feedback_text', required=False, type=unicode, location='json')
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
        'success': fields.Boolean,
        'counter': fields.Integer,
        'has_counter': fields.Boolean
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
            feedback = FeedbackModel.create(args['nps_score'], args['field_responses'], \
                    instance, args.get('feedback_text'), customer_details)
        except FeedbackException:
            abort_error(4004)

        return {'success': True, 'counter': feedback.counter, 'has_counter': feedback.has_counter}

class FeedbackTimelineExport(Resource):

    get_fields = {
        'error': fields.Boolean(default=False),
        'csv_url': fields.String,
    }

    get_parser = reqparse.RequestParser()
    # nps score related args (not required)
    get_parser.add_argument('nps_score_start', required=False, type=nps_score_type, location='args')
    get_parser.add_argument('nps_score_end', required=False, type=nps_score_type, location='args')
    # start & end date for date based filtering (required)
    get_parser.add_argument('start_date', required=True, type=date_arg, location='args')
    get_parser.add_argument('end_date', required=True, type=date_arg, location='args')
    # form ID filter (required)
    get_parser.add_argument('form_id', required=True, type=unicode, location='args')

    @marshal_with(get_fields)
    @login_required('merchant')
    def get(self):
        args = self.get_parser.parse_args()

        # NPS score filters
        nps_score_start = nps_score_end = None
        if args['nps_score_start'] and args['nps_score_end']:
            nps_score_start = args['nps_score_start']
            nps_score_end = args['nps_score_end']

        # add time based filters
        start_date = args['start_date']
        end_date = args['end_date']

        # list of instance IDs associated with given form IDs
        form = form_id_exists(args['form_id'])
        instances = []
        instances_ = InstanceModel.objects.filter(form=form)
        instances.extend(instances_)

        # get the feedbacks
        feedbacks_, all_start_date, all_end_date = FeedbackModel.get_timeline(
                        merchant = g.user.merchant,
                        nps_score_start = nps_score_start,
                        nps_score_end = nps_score_end,
                        start_date = start_date,
                        end_date = end_date,
                        instances = instances
                    )

        # contructing list of dicts for CSVs
        form_fields = dict([(str(i.id), i.text) for i in form.fields]) # dict of titles of form fields
        feedbacks = [] # this list will contain dicts of all feedbacks for csv
        for f in feedbacks_:
            # all feedback details excluding the responses
            f_ = {

                # general feedback details
                'Feedback Text': get_value('feedback_text', f),
                'Feedback Score': get_value('nps_score', f),
                
                # date & time info
                'Date': get_value('received_at', f).strftime('%d-%m-%Y'),
                'Time': get_value('received_at', f).strftime('%H:%M'),

                # customer details
                'Customer Name': get_value('customer.name', f),
                'Customer Mobile': get_value('customer.mobile', f),
                'Customer E-mail': get_value('customer.email', f),
                
                # form and instance details
                'Form Name': get_value('form_instance.form.name', f),
                'Instance Name': get_value('form_instance.name', f),
                'Instance Location': get_value('form_instance.location', f),

            }
            # adding the details of the responses of the feedback
            responses = {}
            for k,v in form_fields.items():
                responses[v] = f.field_responses.get(k)
            f_.update(responses)

            # appending to the list of all feedbacks
            feedbacks.append(f_)

        # keys for the CSV file
        keys = [
            'Date',
            'Time',
            'Customer Name',
            'Customer Mobile',
            'Customer E-mail',
            'Form Name',
            'Instance Name',
            'Instance Location',
            'Feedback Text',
            'Feedback Score'
        ]
        # adding the title of the questions of the form as CSV columns
        for title in form_fields.values():
            keys.append(title)
        # writing to a StringIO object
        f = StringIO.StringIO()
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writer.writerow(keys)
        dict_writer.writerows(feedbacks)

        # uploading to S3
        headers = {'Content-Disposition': 'attachment; filename=timeline-export.csv'}
        key_name = 'timeline-export-{0}.csv'.format(g.user.merchant.id)
        url = upload_s3(f, key_name, 'application/octet-stream', 'ingage-csv-exports', headers)

        return {'csv_url': url}


class FeedbackTimeline(Resource):

    get_fields = {
        'error': fields.Boolean(default=False),
        'total_pages': fields.Integer,
        'total_results': fields.Integer,
        'current_page': fields.Integer,
        'rpp': fields.Integer,
        'start_date': fields.DateTime,
        'end_date': fields.DateTime,
        'all_start_date': fields.DateTime,
        'all_end_date': fields.DateTime,
        'feedbacks': fields.List(fields.Nested(feedback_obj))
    }

    get_parser = reqparse.RequestParser()
    # pagination related args (required)
    get_parser.add_argument('page', required=True, type=int, location='args')
    get_parser.add_argument('rpp', required=True, type=int, location='args')
    # nps score related args (not required)
    get_parser.add_argument('nps_score_start', required=False, type=nps_score_type, location='args')
    get_parser.add_argument('nps_score_end', required=False, type=nps_score_type, location='args')
    # start & end date for date based filtering (not required)
    get_parser.add_argument('start_date', required=False, type=date_arg, location='args')
    get_parser.add_argument('end_date', required=False, type=date_arg, location='args')
    # form ID filter (not required)
    get_parser.add_argument('form_ids', required=False, type=unicode, location='args')

    @marshal_with(get_fields)
    @login_required('merchant')
    def get(self):
        args = self.get_parser.parse_args()

        # number of results to skip (using mongoengine)
        skip_number = (args['page'] - 1) * args['rpp']

        # NPS score filters
        nps_score_start = nps_score_end = None
        if args['nps_score_start'] and args['nps_score_end']:
            nps_score_start = args['nps_score_start']
            nps_score_end = args['nps_score_end']

        # add time based filters if given as arguments
        start_date = end_date = None
        if args['start_date'] and args['end_date']:
            start_date = args['start_date']
            end_date = args['end_date']

        # list of instance IDs associated with given form IDs
        instances = None
        if args['form_ids']:
            form_ids = args['form_ids'].split(',')
            instances = []
            for id in form_ids:
                form = form_id_exists(id)
                instances_ = InstanceModel.objects.filter(form=form)
                instances.extend(instances_)

        # get the feedbacks
        feedbacks, all_start_date, all_end_date = FeedbackModel.get_timeline(
                        merchant = g.user.merchant,
                        nps_score_start = nps_score_start,
                        nps_score_end = nps_score_end,
                        start_date = start_date,
                        end_date = end_date,
                        instances = instances
                    )

        # start date and end date (with the current filters but without page numbers)
        start_date = feedbacks.skip(len(feedbacks)-1).limit(1)[0].received_at
        end_date = feedbacks[0].received_at

        # pagination related stuff
        total_results = feedbacks.count() # total number of feedbacks returned
        feedbacks = feedbacks.skip(skip_number).limit(args['rpp']) # skipping on basis of page number
        total_pages = math.ceil(float(total_results) / args['rpp']) # total number of pages formed w.r.t rpp

        return {
            'feedbacks': feedbacks,
            'total_pages': total_pages,
            'current_page': args['page'],
            'rpp': args['rpp'],
            'total_results': total_results,
            'start_date': start_date,
            'end_date': end_date,
            'all_start_date': all_start_date,
            'all_end_date': all_end_date,
        }


class FeedbackAnalytics(Resource):

    get_fields = {
        'error': fields.Boolean(default=False),
        'analytics': fields.List(fields.Nested(analytics_obj)),
        'no_analytics': fields.Boolean(default=False)
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

        # check if all numbers are `0` in analytics
        numbers = []
        for analytic in  analytics.values():
            for number in analytic['numbers'].values():
                numbers.append(number['number'])
        no_analytics = False if sum(numbers) > 0 else True

        return {'analytics': [v for k,v in analytics.items()], 'no_analytics': no_analytics}

## Registering Endpoints

# merchant dashboard
api.add_resource(FormList, '/dashboard/forms')
api.add_resource(Form, '/dashboard/forms/<form_id>')
api.add_resource(FormInstanceList, '/dashboard/forms/<form_id>/instances')
api.add_resource(FormInstance, '/dashboard/forms/<form_id>/instances/<instance_id>')
api.add_resource(FeedbackTimeline, '/dashboard/timeline')
api.add_resource(FeedbackTimelineExport, '/dashboard/timeline/csv_export')
api.add_resource(FeedbackAnalytics, '/dashboard/forms/<form_id>/analytics')

# customer facing
api.add_resource(CustomerFeedback, '/customer/feedback/<instance_id>')
