# -*- coding: utf-8 -*-

import re
from django import forms
from django.db import models
from django.db.models import fields
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


#=================================================================================
class ColorPickerWidget(forms.TextInput):
    class Media:
        js = (
            settings.STATIC_URL + 'colorpicker/colorPicker.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(ColorPickerWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        return mark_safe(u'''
            <input type="text" id="id_%(name)s" name="%(name)s" value="%(value)s" style="background-color:%(value)s;border:0px;" onclick="colorPicker(event)" />
            ''' % dict(name=name, value=value))


#==============================================================================
class RGBColorField(models.CharField):
    """
    Color field that stores a color in HTML hexadecimal format
    """
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(RGBColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(RGBColorField, self).formfield(**kwargs)

    def clean(self, value, model_instance):
        value = super(RGBColorField, self).clean(value, model_instance)
        if value in fields.EMPTY_VALUES:
            return ''
        if value[0] != '#':
            value = '#' + value
        value = smart_unicode(value)
        value_length = len(value)
        if value_length != 7 or not re.match('^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', value):
            raise forms.ValidationError(_('This is an invalid color code: %s' % value))
        return value
