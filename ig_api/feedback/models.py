# -*- coding: utf-8 -*-
from ig_api import db


## Helpers


class FormException(Exception):
    def __init__(self, message):
        self.message = message


class InstanceException(Exception):
    def __init__(self, message):
        self.message = message


## Models


class FormModel(db.Document):
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    
    # which merchant is the form associated with?
    merchant = db.ReferenceField('MerchantModel', required=True)

    meta = {'collection': 'forms'}

    @staticmethod
    def create(name, description, merchant):
        form = FormModel(name=name, description=description, merchant=merchant)
        try:
            form.save()
        except db.ValidationError:
            raise FormException('Form data provided was wrong')
        
        return form

    def create_instance(self, name, description, location):
        """name, description & location of the instance are to be provided."""
        instance = InstanceModel(name=name, description=description, location=location, form=self)
        try:
            instance.save()
        except db.ValidationError:
            raise InstanceException('Instance data provided was wrong.')

        return instance

    def __repr__(self):
        return '<FormModel: {0} ({1})>'.format(self.name, self.merchant.name)


class InstanceModel(db.Document):
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    location = db.StringField(required=True)

    # which form is the instance associated with?
    form = db.ReferenceField('FormModel', required=True)

    meta = {'collection': 'intances'}

    def __repr__(self):
        return '<InstanceModel: {0}>'.format(self.name)
