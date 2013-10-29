# -*- coding: utf-8 -*-
from ig_api import db, app


class MerchantModel(db.Document):
    name = db.StringField(required=True)
    address = db.StringField(required=True)
    contact_number = db.StringField()
    logo = db.URLField()

    meta = {'collection': 'merchants'}

    @staticmethod
    def create_merchant(name, address, contact_number=None):
        details = locals()
        # default logo image set as logo
        # this is done as logo is set using a PUT request only after merchant has been created
        details['logo'] = app.config['AWS_S3_DEFAULT_LOGO_URL']
        merchant = MerchantModel(**details)
        merchant.save()

        return merchant

    def __repr__(self):
        return '<MerchantModel: %s>' % self.name
