# -*- coding: utf-8 -*-
import datetime

from bson.objectid import ObjectId

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


class FormFieldSubModel(db.EmbeddedDocument):
        FIELD_TYPES = (
            ('YN', 'YES/NO FIELD'),
            ('ST', 'STAR RATING FIELD'),
            ('MT', 'MULTIPLE FIELD'),
            ('TT', 'TEXT FIELD')
        )

        field_type = db.StringField(max_length=2, choices=FIELD_TYPES, required=True)
        text = db.StringField(required=True)
        choices = db.ListField(db.StringField()) # only used in case of MULTIPLE FIELD
        id = db.ObjectIdField(required=True, default=ObjectId)

        def validate(self, *args, **kwargs):
            # check there are the correct amount of choices in case of multiple field
            if self.field_type == 'MT': # in case of MULTIPLE FIELD
                if len(self.choices) < 2 or len(self.choices) > 5:
                    raise db.ValidationError(message='Number of choices provided for multiple field should be between 2 and 5.')

            # run the original validation method
            super(FormFieldSubModel, self).validate(*args, **kwargs)

        def validate_customer_response(self, response):
            """Validates the response given by a customer for a particular field.
            Raises a `ValueError` if the response given is wrong. In case of no error
            it just return `None`
            """
            # YES/NO FIELD
            if self.field_type == 'YN':
                if not response in ['YES', 'NO']:
                    raise ValueError('The response to a Yes/No Field can only be "YES" or "NO". Case-Sensitive.')
    
            # STAR RATING FIELD
            if self.field_type == 'ST':
                if not int(response) in [1, 2, 3, 4, 5]:
                    raise ValueError('The response to a Star Rating Field can only be among [1,2,3,4,5]. Integer.')

            # MULTIPLE FIELD
            if self.field_type == 'MT':
                if not response in self.choices:
                    raise ValueError('The response to a Mutliple Field should be among one of the choices of the field.')

            # TEXT FIELD
            if self.field_type == 'TT':
                if not type(response) is str and not type(response) is unicode:
                    raise ValueError('The response to a Text Field can only be a string of unicode or str type.')

        def __repr__(self):
            return '<FormFieldSubModel: {0} ({1})>'.format([i[1] for i in self.FIELD_TYPES if i[0] == self.field_type][0], self.text)

class FormModel(db.Document):
    # basic info about the form
    name = db.StringField(required=True)
    description = db.StringField(required=True)

    # fields comprising of the form
    fields = db.ListField(db.EmbeddedDocumentField(FormFieldSubModel))
    
    # heading text for 'Your Details', 'NPS Score', 'Tell Us More' sections
    customer_details_heading = db.StringField(required=True)
    feedback_heading = db.StringField(required=True)
    nps_score_heading = db.StringField(required=True)

    # which merchant is the form associated with?
    merchant = db.ReferenceField('MerchantModel', required=True)

    meta = {'collection': 'forms'}

    def get_analytics(self, instance_ids, start_date=None, end_date=None):
        """Returns the analytics for the form fields.

        Keyword Arguments:
        instance_ids -- ids of the instance for which the analytics are needed.
        start_date -- date (inclusive) from which the analytics are needed.
        end_date -- date (inclusive) till which the analytics are needed.

        Note: 1. No analytics are generated for the text field.
              2. If the analytics need to be filtered on basis of time both
                 `start_date` and `end_date` need to be specified.
              3. The value of `start_date` and `end_date` should be in UTC time.
        """
        # all the feedbacks attached with the given instance ids
        if start_date and end_date: # add filter if `start_date` and `end_date` are provided
            feedbacks = FeedbackModel.objects.filter(received_at__gte=start_date, received_at__lte=end_date,
                    form_instance__in=instance_ids)
        else:
            feedbacks = FeedbackModel.objects.filter(form_instance__in=instance_ids)
        # this dict will contain all the analytics and the corresponding fields
        responses = {}
        # adding the `FormFieldSubModel` instance in the `responses` dict
        for field in self.fields:
            # the analytics will not be provided for TEXT FIELD
            if field.field_type != 'TT':
                responses[str(field.id)] = {
                    'responses': [],
                    'field': field
                }
        # adding the actual list of responses to the `responses` dict
        for feedback in feedbacks:
            for f_id, response in feedback.field_responses.items():
                if str(f_id) in responses:
                    responses[str(f_id)]['responses'].append(response)
        # counting the number of responses for providing as analytics
        for f_id, response in responses.items():
            #TODO: this is just a temproary work around
            colors = ['#4D5361', '#FFB553', '#3EBFBE', '#949FB2', '#FA4444', '#736d64']
            if response['field'].field_type == 'YN':
                responses[f_id]['numbers'] = {
                    'YES': {
                        'number': response['responses'].count('YES'),
                        'color': colors.pop(),
                        'text': 'YES'
                    },
                    'NO': {
                        'number': response['responses'].count('NO'),
                        'color': colors.pop(),
                        'text': 'NO'
                    }
                }
                responses[f_id]['total_responses'] = sum([i['number'] for i in responses[f_id]['numbers'].values()])
            if response['field'].field_type == 'ST':
                responses[f_id]['numbers'] = {
                    '1': {
                        'number': response['responses'].count('1'),
                        'color': colors.pop(),
                        'text': '1 stars'
                    },
                    '2': {
                        'number': response['responses'].count('2'),
                        'color': colors.pop(),
                        'text': '2 stars'
                    },
                    '3': {
                        'number': response['responses'].count('3'),
                        'color': colors.pop(),
                        'text': '3 stars'
                    },
                    '4': {
                        'number': response['responses'].count('4'),
                        'color': colors.pop(),
                        'text': '4 stars'
                    },
                    '5': {
                        'number': response['responses'].count('5'),
                        'color': colors.pop(),
                        'text': '5 stars'
                    },
                }
                responses[f_id]['total_responses'] = sum([i['number'] for i in responses[f_id]['numbers'].values()])
            if response['field'].field_type == 'MT':
                responses[f_id]['numbers'] = {}
                for choice in response['field'].choices:
                    responses[f_id]['numbers'][choice] = {
                            'number': response['responses'].count(choice),
                            'color': colors.pop(),
                            'text': choice
                    }
                    responses[f_id]['total_responses'] = sum([i['number'] for i in responses[f_id]['numbers'].values()])

        return responses

    @staticmethod
    def create(name, description, customer_details_heading, feedback_heading, nps_score_heading, fields, merchant):
        """Creates a new form instance.

        The `fields` keyword argument will take up a list with `FormFieldSubModel` instances. The order of these
        instances in the `fields` list will decide the order for the customer facing form.

        For now a feedback form can have a maximum of 4 fields.
        """

        form = FormModel(name=name, description=description, merchant=merchant, customer_details_heading=customer_details_heading,
                feedback_heading=feedback_heading, nps_score_heading=nps_score_heading, fields=fields)
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
    # nps score and feedback text
    nps_score = db.IntField(required=True, choices=range(1,11))
    feedback_text = db.StringField(required=True)

    # customer response to the different fields of the form
    field_responses = db.DictField(required=True)

    # time the feedback was received at (utc time)
    received_at = db.DateTimeField(required=True, default=datetime.datetime.utcnow)

    # which customer is feedback associated with?
    customer = db.ReferenceField('CustomerModel')

    # which instance is feedback associated with?
    form_instance = db.ReferenceField('InstanceModel', required=True)

    # which merchant is feedback associated with?
    merchant = db.ReferenceField('MerchantModel', required=True)

    meta = {'collection': 'feedbacks'}

    @staticmethod
    def get_timeline(merchant, nps_score_start=None, nps_score_end=None, start_date=None, end_date=None, instances=None):
        """Returns the MongoEngine queryset for the timeline filtered on basis of
        various filters ordered in a reverse chronogical order.

        Note: This method does not take care of any sort of filters. They can be implemented using the
              queryset returned by this method.

        Keyword Arguments:
        
        merchant: (required) Whose timeline is to be returned?

        nps_score_start: (optional) Starting (inclusive) range of NPS score. (between 0 to 10)
        nps_score_end (optional) Ending (inclusive) range of NPS score. (between 0 to 10)

        start_date: (optional) Results returned would be from dates equal to or greater than this date. (datetime.datetime)
        end_date: (optional) Results returned would be from dates equal to or less than this date. (datetime.datetime)

        instances: (optional) List of instances of whose results need to be returned.
        """

        # get all feedbacks (without a filter) for the merchant
        feedbacks = FeedbackModel.objects.filter(merchant=merchant)

        # filter on basis of nps score if provided
        if nps_score_start and nps_score_end:
            feedbacks = FeedbackModel.objects.filter(merchant=merchant, nps_score__gte=args['nps_score_start'], 
                    nps_score__lte=args['nps_score_end'])

        # filter on basis of start and end date
        if start_date and end_date:
            feedbacks = feedbacks.filter(merchant=merchant, received_at__gte=start_date,
                    received_at__lte=end_date)

        # filter on basis of instances
        if instances:
            feedbacks = feedbacks.filter(form_instance__in=instances)

        # order the feedback query set by received date
        feedbacks = feedbacks.order_by("-received_at")

        return feedbacks

    @property
    def responses(self):
        """This method returns a list of responses given to the
        feedback with the details of fields the responses are
        associated with.
        """

        form = self.form_instance.form 
        # list of dictionaries of responses
        responses = []

        # iterating over all the responses of the feedback
        for f_id, response in self.field_responses.items():
            # check for the field the response is associated with
            for field in form.fields:
                if str(field.id) == f_id:
                    responses.append({
                        'text': field.text,
                        'type': field.field_type,
                        'response': response,
                        'id': f_id
                    })
        return responses

    @staticmethod
    def create(nps_score, feedback_text, field_responses, form_instance, customer_details=None):
        # validate the responses of the fields of the form
        form = form_instance.form
        for field in form.fields:
            # validate the response of the field
            response = field_responses.get(str(field.id))
            if not response:
                raise FeedbackException('Response to all the fields of the form has not been provided.')
            # check if correct response is given to all of the fields
            try:
                field.validate_customer_response(response)
            except ValueError:
                raise FeedbackException('Correct response to one or more fields has not been given.')

        # feedback form object
        feedback = FeedbackModel(nps_score=nps_score, feedback_text=feedback_text, field_responses=field_responses,
                form_instance=form_instance, merchant=form_instance.form.merchant)

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
