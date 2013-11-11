# -*- coding: utf-8 -*-
import datetime

from flask.ext.restful import reqparse, fields

class FileStorageArgument(reqparse.Argument):
    """This argument class for flask-restful will be used in
    all cases where file uploads need to be handled."""
    
    def convert(self, value, op):
        if self.type is FileStorage:  # only in the case of files
            # this is done as self.type(value) makes the name attribute of the
            # FileStorage object same as argument name and value is a FileStorage
            # object itself anyways
            return value

        # called so that this argument class will also be useful in
        # cases when argument type is not a file.
        super(FileStorageArgument, self).convert(*args, **kwargs)


class DateTimeField(fields.Raw):
    """Formats the DateTime object in the ISO8016 format for JSON."""

    def format(self, value):
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        raise MarshallingException("Only DateTime objects can be marshalled.")


def DateTimeFieldType(value):
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
