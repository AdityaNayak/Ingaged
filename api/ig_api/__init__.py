# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_sslify import SSLify
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api as FlaskRestfulAPI

## config
current_dir = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
MONGODB_SETTINGS = {
    'DB': 'ingage-develop',
    'USERNAME': None,
    'PASSWORD': None,
    'HOST': None,
    'PORT': None
}
if os.environ.get('MONGOHQ_URL'): # if on heroku
    user, password_host, port_db = os.environ.get('MONGOHQ_URL')[10:].split(':')
    password, host = password_host.split('@')
    port, db = port_db.split('/')
    MONGODB_SETTINGS['USERNAME'] = user
    MONGODB_SETTINGS['PASSWORD'] = password
    MONGODB_SETTINGS['HOST'] = host
    MONGODB_SETTINGS['PORT'] = int(port)
    MONGODB_SETTINGS['DB'] = db
LOGO_ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
IMAGE_CONTENT_TYPES = { # content types of different images. will be used while uploading images to S3.
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}
LOGO_MAX_FILE_SIZE = 1 * 1024 * 1024 # 1MB
AWS_ACCESS_KEY_ID = 'AKIAJPKFYAQXRHIIIPNA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_S3_LOGO_BUCKET = 'logos-dev-ingage'
AWS_S3_DEFAULT_LOGO_FILE = os.path.join(current_dir, 'config/default-logo.png') # path to default logo of the merchant. absolute path.
AWS_S3_DEFAULT_LOGO_KEY_NAME = 'default-logo.png'
AWS_S3_DEFAULT_LOGO_URL = 'https://{0}.s3.amazonaws.com/{1}'.format(AWS_S3_LOGO_BUCKET, AWS_S3_DEFAULT_LOGO_KEY_NAME)
ADMIN_EMAIL = 'me@rishabhverma.me'
TRANSACTIONAL_EMAILS = {
    'new_merchant_new_user': { # this is sent to a new user who is created while creating a merchant
        'subject': 'Wecome to InGage Dashboard',
        'template': 'emails/new_merchant_user.html',
        'from': 'InGage <hello@ingagelive.com>'
    },
    'signup_request': { # this is sent to the admin when a user requests for a sign up
        'subject': 'Sign Up Request for InGage',
        'template': 'emails/signup_request.html',
        'from': 'InGage <hello@ingagelive.com>'
    },
}

## app initilization
app = Flask(__name__)
app.config.from_object(__name__)

## extensions
db = MongoEngine(app)
if os.environ.get('MONGOHQ_URL'): # if on heroku
    db.connection[MONGODB_SETTINGS['DB']].authenticate(MONGODB_SETTINGS['USERNAME'], MONGODB_SETTINGS['PASSWORD'])
    sslify = SSLify(app)
api = FlaskRestfulAPI(app)


# CORS headers
@app.after_request
def add_access_control_headers(response):
    """Adds the required access control headers"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization,Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET,PUT,DELETE'
    response.headers['Cache-Control'] = 'No-Cache'
    return response


## endpoints & models

# authentication
from ig_api.authentication.api import *
from ig_api.authentication.models import *

# merchants
from ig_api.merchants.api import *
from ig_api.merchants.models import *

# feedback (dashboard & customer facing feedback collection)
from ig_api.feedback.api import *
from ig_api.feedback.models import *

# extras (miscellaneous stuff)
from ig_api.misc.api import *
from ig_api.misc.models import *
