# -*- coding: utf-8 -*-
from flask import g
from flask.ext.restful import Resource, reqparse, fields, marshal_with
from bson.objectid import ObjectId
from pymongo.errors import InvalidId

from ig_api import api, db
from ig_api.error_codes import abort_error
from ig_api.authentication import login_required
from ig_api.feedback.models import FormModel, InstanceModel, FormException, InstanceException


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
        abort_error(4001)

    return instance


## Different objects to be returns (to be used with `marshal_with`)
form_obj = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String
}

instance_obj = {
    'id': fields.String,
    'name': fields.String,
    'description': fields.String,
    'location': fields.String
}


## Endpoints


class FormList(Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', required=True, type=unicode, location='json')
    post_parser.add_argument('description', required=True, type=unicode, location='json')

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
        forms = FormModel.objects.all()

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


## Registering Endpoints

# merchant dashboard
api.add_resource(FormList, '/dashboard/forms')
api.add_resource(Form, '/dashboard/forms/<form_id>')
api.add_resource(FormInstanceList, '/dashboard/forms/<form_id>/instances')
api.add_resource(FormInstance, '/dashboard/forms/<form_id>/instances/<instance_id>')
