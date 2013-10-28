# -*- coding: utf-8 -*-
from flask.ext.restful import Resource

from ig_api import api
from ig_api.authentication import login_required

__all__ = ['AdminUserCredentialCheck', ]


class AdminUserCredentialCheck(Resource):

    @login_required('admin')
    def get(self):
        return {'error': False, 'correct': True}


## Registering Endpoints

# admin panel
api.add_resource(AdminUserCredentialCheck, '/admin/auth/check_credentials')
