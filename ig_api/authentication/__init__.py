# -*- coding: utf-8 -*-
from functools import wraps

from flask import g, request

from ig_api import db
from ig_api.error_codes import abort_error
from ig_api.authentication.models import AdminUser


class login_required(object):
    """This decorator checks the credentials (in HTTP Basic Auth).

    In case of correct credentials it adds the user object as an attribute
    of the `g` variable provided by flask.
    
    Keyword Arguments (for decorator):
    access -- 'admin' or 'merchant'
    """

    def __init__(self, access):
        self.access = access

    def __call__(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # username & password from 'Authentication' header
            auth = request.authorization
            if not auth:
                abort_error(1000)

            # find user with given username and compare passwords
            user_models = {'admin': AdminUser}
            user_model = user_models[self.access]
            try:
                user = user_model.objects.get(username=auth.username)
            except db.DoesNotExist: # user does not exist
                abort_error(1000)
            if not user.check_password(auth.password): # password is not correct
                abort_error(1000)

            # attach user object as attribute of `g`
            g.user = user

            return f(*args, **kwargs)

        return decorated
