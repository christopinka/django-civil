# -*- coding: utf-8 -*-

import base64
from django.db.models import fields

#==============================================================================
class Base64Field(models.TextField):
    """
    A base64 field to store binary data into a text field in django.

        class Foo(models.Model):
            data = Base64Field()
        foo = Foo()
        foo.data = 'Hello world!'
        print foo.data # will 'Hello world!'
        print foo.data_base64 # will print 'SGVsbG8gd29ybGQh\n'

    """
    __metaclass__ = models.SubfieldBase

    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))
