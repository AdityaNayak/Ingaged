# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.mongoengine import MongoEngine

## config
DEBUG = True
MONGODB_SETTINGS = {'DB': 'ingage-develop'}

## app initilization
app = Flask(__name__)
app.config.from_object(__name__)

## extensions
db = MongoEngine(app)
