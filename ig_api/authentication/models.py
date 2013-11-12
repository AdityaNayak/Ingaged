# -*- coding: utf-8 -*-
import md5

from ig_api import db
from ig_api.helpers import send_trans_email


## Helpers


class BaseUser(object):
    """This class has all the methods which are common to any kind of a user."""

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        """Stores the md5 hash of the given password as an object attribute."""
        self._password = md5.md5(password).hexdigest()

    def check_password(self, password):
        """Compares a given password with the actual stored password."""
        return self._password == md5.md5(password).hexdigest()


class MerchantUserException(Exception):
    def __init__(self, message):
        self.message = message


## Models


class AdminUserModel(BaseUser, db.Document):
    name = db.StringField(required=True)
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True)
    _password = db.StringField(required=True)

    meta = {'collection': 'admin_users'}

    @staticmethod
    def create_admin(name, username, email, password):
        """Creates a new admin user.
        
        Note: Error handling not taken care of.
        """
        admin = AdminUserModel(name=name, username=username, email=email)
        admin.password = password # cannot set while initializing as the hash of the password needs to be saved
        admin.save()
        return admin

    def __repr__(self):
        return '<AdminUserModel: %s (%s)>' % (self.name, self.username)


class MerchantUserModel(BaseUser, db.Document):
    name = db.StringField(required=True)
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    _password = db.StringField(required=True)

    # which merchant is this user associated with?
    merchant = db.ReferenceField('MerchantModel', required=True)

    meta = {'collection': 'merchant_users'}

    # TODO: currently username does not have a merchant specific name space. explore.

    @staticmethod
    def create(name, username, email, password, merchant):
        """Creates a new user under the given merchant."""
        # create new user 
        user = MerchantUserModel(name=name, username=username, email=email, merchant=merchant)
        user.password = password # cannot set while initializing as the hash of password needs to be saved
        try:
            user.save()
        except (db.ValidationError, db.NotUniqueError):
            raise MerchantUserException('Merchant user data provided was wrong.')

        # send e-Mail
        email_vars = {
            'name': name,
            'username': username,
            'email': email,
            'password': password
        }
        send_trans_email('new_merchant_new_user', user.name, user.email, email_vars)

        return user

    def __repr__(self):
        return '<MerchantUserModel: %s (%s)>' % (self.name, self.username)
