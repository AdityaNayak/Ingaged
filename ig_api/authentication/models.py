# -*- coding: utf-8 -*-
import md5

from ig_api import db


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


class AdminUser(BaseUser, db.Document):
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
        admin = AdminUser(name=name, username=username, email=email)
        admin.password = password # cannot set while initializing as the hash of the password needs to be saved
        admin.save()
        return admin

    def __repr__(self):
        return '<AdminUser: %s (%s)>' % (self.name, self.username)
