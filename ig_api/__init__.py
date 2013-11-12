# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api as FlaskRestfulAPI

## config
current_dir = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
MONGODB_SETTINGS = {'DB': 'ingage-develop'}
LOGO_ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
IMAGE_CONTENT_TYPES = { # content types of different images. will be used while uploading images to S3.
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}
LOGO_MAX_FILE_SIZE = 1 * 1024 * 1024 # 1MB
AWS_ACCESS_KEY_ID = 'AKIAJUWCXRMPSG23JT5A'
AWS_SECRET_ACCESS_KEY = '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'
AWS_S3_LOGO_BUCKET = 'ingage-logos-development'
AWS_S3_DEFAULT_LOGO_FILE = os.path.join(current_dir, 'config/default-logo.png') # path to default logo of the merchant. absolute path.
AWS_S3_DEFAULT_LOGO_KEY_NAME = 'default-logo.png'
AWS_S3_DEFAULT_LOGO_URL = 'https://{0}.s3.amazonaws.com/{1}'.format(AWS_S3_LOGO_BUCKET, AWS_S3_DEFAULT_LOGO_KEY_NAME)
TRANSACTIONAL_EMAILS = {
    'new_merchant_new_user': { # this is sent to a new user who is created while creating a merchant
        'subject': 'Wecome to InGage Dashboard',
        'template': 'emails/new_merchant_user.html',
        'from': 'InGage <me@rishabhverma.me>',
    },
}

## app initilization
app = Flask(__name__)
app.config.from_object(__name__)

## extensions
db = MongoEngine(app)
api = FlaskRestfulAPI(app)

## endpoints & models

# authentication
from ig_api.authentication.api import *
from ig_api.authentication.models import *

# merchants
from ig_api.merchants.api import *
from ig_api.merchants.models import *
