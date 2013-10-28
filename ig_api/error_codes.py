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
        '1000': 'Username/Password are not provided or incorrect.'

}
