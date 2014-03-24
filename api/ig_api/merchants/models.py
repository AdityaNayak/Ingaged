# -*- coding: utf-8 -*-
import datetime

from ig_api import db, app
from ig_api.authentication.models import MerchantUserModel
from ig_api.authentication.models import MerchantUserException


## Helpers


class MerchantException(Exception):
    def __init__(self, message):
        self.message = message


## Models


class MerchantModel(db.Document):
    name = db.StringField(required=True)
    address = db.StringField(required=True)
    contact_number = db.StringField()
    logo = db.URLField()

    # for e-mail based notifications for feedbacks below threshold
    nps_notifs = db.BooleanField(required=True, default=False)
    notif_emails = db.ListField(field=db.EmailField())
    nps_threshold = db.IntField()

    # will be used for payments
    current_balance = db.FloatField(required=True, default=0.0)

    meta = {'collection': 'merchants'}

    @staticmethod
    def create_merchant(name, address, user_details, contact_number=None):
        """Creates a new merchant and a new user attached with the merchant.
        
        Note: Keys of `user_details` dict should be same as fields of
              `MerchantUserModel`
        """
        details = locals()

        ## create merchant
        # default logo image set as logo
        # this is done as logo is set using a PUT request only after merchant has been created
        details['logo'] = app.config['AWS_S3_DEFAULT_LOGO_URL']
        merchant = MerchantModel(**details)
        try:
            merchant.save()
        except (db.ValidationError, db.NotUniqueError):
            raise MerchantException('Merchant data provided was wrong.')

        ## create merchant user
        user_details['merchant'] = merchant
        try:
            user = MerchantUserModel.create(**user_details)
        except MerchantUserException as e:
            merchant.delete() # delete the merchant created in the last step as that is no longer needed
            raise e

        return merchant

    def __repr__(self):
        return '<MerchantModel: {0}>'.format(self.name)


class PaymentModel(db.Document):
    METHOD_CHOICES = (
        (1, 'Cheque'),
        (2, 'Cash')
    )

    amount = db.FloatField(required=True)
    method = db.IntField(required=True, choices=METHOD_CHOICES)
    notes = db.StringField(required=False)
    received_at = db.DateTimeField(required=True)
    key_in_at = db.DateTimeField(required=True, default=datetime.datetime.utcnow)

    # which merchant is the payment associated with?
    merchant = db.ReferenceField('MerchantModel', required=True)

    meta = {'collection': 'merchant_payments'}

    @staticmethod
    def key_in(amount, method, received_at, merchant, notes=None):
        """Keys in the payment in the system corresponding to the given merchant.
        Also increments the current balance of the merchant by the amount
        of the payment.

        Returns the payment object (PaymentModel).

        Keyword Arguments:
        amount -- Float value of the amount.
        method -- Integer. Check `PaymentModel.METHOD_CHOICES` for the possible values.
        received_at -- DateTime the payment was received at. This is different from the time
                       when the payment was keyed into the system which is set automatically
                       as the current system time.
        notes -- Any custom notes which need to be attached.
        merchant -- Object of the merchant with which the payment needs to be associated.
        """
        details = locals()

        # create and save payment object
        payment = PaymentModel()
        for k,v in details.items():
            setattr(payment, k, v)
        payment.save()

        #TODO: mongodb two phase commits should be taken care of later on.
        # increment the merchant balance and save
        merchant = details.pop('merchant')
        merchant.current_balance += payment.amount
        merchant.save()

        return payment

    def __repr__(self):
        return '<PaymentModel: {0} - {1} ({2})>'.format(self.amount, self.received_at, self.merchant.name)
