# -*- coding: utf-8 -*-
from flask.ext.restful import Resource, reqparse

from ig_api import api
from ig_api.error_codes import abort_error
from ig_api.misc.models import SignUpRequestModel, SignUpRequestException

## Endpoints

class SignUpUserRequest(Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', required=True, type=unicode, location='json')
    post_parser.add_argument('email', required=True, type=unicode, location='json')
    post_parser.add_argument('phone', required=False, type=unicode, location='json')

    def post(self):
        args = self.post_parser.parse_args()
        try:
            request = SignUpRequestModel.create(**args)
        except SignUpRequestException:
            abort_error(5000)

        return {'success': True}

## Registering Endpoints

# dashboard
api.add_resource(SignUpUserRequest, '/dashboard/signup_request')
