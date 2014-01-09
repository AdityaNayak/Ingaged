# -*- coding: utf-8 -*-
"""All the error codes with a human readable message are listed here."""
from flask.ext.restful import abort

def abort_error(error_code, http_code=400):
    """This is used to abort a request in-case of some problem, error etc.
    
    Keyword Arguments:
    error_code -- code of the error. should exist in `ig_api.error_codes.ERROR_CODES`
    http_code -- http_code of the error. defaults to 400.

    Note: We will be keeping HTTP status code for every error produced as 400 (except 404
          not found). The errors will be recognized by the unique error codes.
    """
    abort(http_code, error=True, message=ERROR_CODES[str(error_code)], code=error_code)


ERROR_CODES = {

        # authentication (1000 - 1999)
        '1000': 'Username/Password are not provided or incorrect.', # http basic auth

        # merchants (2000 - 2999)
        '2000': 'Merchant details provided were not correct.', # while merchant is being edited or created
        '2001': 'Only jpg, jpeg and png are valid extensions for a logo.', # when uploading the logo
        '2003': 'Merchant with the given ID does not exist.', # merchant does not exist
        '2004': 'Payment details provided were not correct.', # while keying in a new payment

        # merchant users (3000 - 3999) only related to merchant user specific action. mainly authentication
        '3000': 'New merchant user information provided is not correct.', # while creating a new merchant

        # feedback (4000 - 4999) related to form creation etc. on dashboard and customer facing feedback collection
        '4000': 'Form data provided was not right.', # while creating the form
        '4001': 'Form(s) with the given ID does not exist.', # form does not exist
        '4002': 'Form instance data provided was not correct.', # while creating a form instance
        '4003': 'Form instance(s) with the given ID does not exist.', # form instance does not exist
        '4004': 'Feedback data submitted is wrong' # while customer is giving feedback

}
