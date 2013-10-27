# -*- coding: utf-8 -*-
"""All the error codes with a human readable message are listed here."""
from flask.ext.restful import abort

def abort_error(error_code):
    """This is used to abort a request in-case of some problem, error etc.
    
    Note: Right now the HTTP status code for every aborted request will be 400.
          Error will be recognized by the unique error codes.
    """
    abort(400, error=True, message=ERROR_CODES[str(error_code)], code=error_code)


ERROR_CODES = {

        # authentication (1000 - 1999)
        '1000': 'Username/Password are not provided or incorrect.'

}
