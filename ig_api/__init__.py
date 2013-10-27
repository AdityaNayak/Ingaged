# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api as FlaskRestfulAPI

## config
DEBUG = True
MONGODB_SETTINGS = {'DB': 'ingage-develop'}

## app initilization
app = Flask(__name__)
app.config.from_object(__name__)

## extensions
db = MongoEngine(app)
api = FlaskRestfulAPI(app)

## endpoints & models
from ig_api.authentication.api import *
from ig_api.authentication.models import *
