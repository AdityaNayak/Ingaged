# -*- coding: utf-8 -*-
import datetime

from ig_api import db


## Helpers


class FormException(Exception):
    def __init__(self, message):
        self.message = message


class InstanceException(Exception):
    def __init__(self, message):
        self.message = message

class FeedbackException(Exception):
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


class FeedbackModel(db.Document):
    text = db.StringField(required=True)
    received_at = db.DateTimeField(required=True, default=datetime.datetime.utcnow)

    # which customer is feedback associated with?
    customer = db.ReferenceField('CustomerModel')

    # which instance is feedback associated with?
    form_instance = db.ReferenceField('InstanceModel', required=True)

    # which merchant is feedback associated with?
    merchant = db.ReferenceField('MerchantModel', required=True)

    meta = {'collection': 'feedbacks'}

    @staticmethod
    def create(text, form_instance, customer_details=None):
        feedback = FeedbackModel(text=text, form_instance=form_instance, merchant=form_instance.form.merchant)

        # create customer object only if customer exists
        customer = None
        if customer_details:
            name = customer_details.get('name')
            mobile = customer_details.get('mobile')
            email = customer_details.get('email')
            customer = CustomerModel(name=name, mobile=mobile, email=email)

        # validate customer & feedback objects
        try:
            feedback.validate()
            if customer:
                customer.validate()
        except db.ValidationError:
            raise FeedbackException('Feedback data provided was wrong.')

        # add customer id to feedback object
        if customer:
            customer.save()
            feedback.customer = customer

        feedback.save()

        return feedback

    def __repr__(self):
        return '<FeedbackModel: {0}>'.format(self.received_at)


class CustomerModel(db.Document):
    name = db.StringField(required=False)
    mobile = db.StringField(required=False)
    email = db.StringField(required=False)

    meta = {'collection': 'customers'}

    def __repr__(self):
        return '<CustomerModel: {0} ({1})>'.format(self.name, self.email)
