# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django.conf import settings
from django.contrib.admin import widgets
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from civil.library.models import BaseModel
from civil.library.fields.code import PythonCodeField
from civil.library.utils.reload import force_reload


#==============================================================================
VALID_CUSTOM_CONTENT_TYPES = {
    'name__in': ['contact'],
}


#==============================================================================
DEFAULT_VALIDATOR_VALUE = """
# Custom validator function here
# def validator(value, instance=None): 
#     #raise Exception("Invalid value")
#     pass
"""

#==============================================================================
class ContentTypeCustomField(BaseModel):

    TYPE_TEXT     = 'text'
    TYPE_INTEGER  = 'int'
    TYPE_FLOAT    = 'float'
    TYPE_DECIMAL  = 'decimal'
    TYPE_TIME     = 'time'
    TYPE_DATE     = 'date'
    TYPE_DATETIME = 'datetime'
    TYPE_BOOLEAN  = 'bool'
    
    DATATYPE_CHOICES = (
        (TYPE_TEXT,     _('text')),
        (TYPE_INTEGER,  _('integer')),
        (TYPE_FLOAT,    _('float')),
        (TYPE_TIME,     _('time')),
        (TYPE_DATE,     _('date')),
        (TYPE_DATETIME, _('datetime')),
        (TYPE_BOOLEAN,  _('boolean')),
    )

    FIELD_TYPES = {
        TYPE_TEXT:     forms.CharField,
        TYPE_INTEGER:  forms.IntegerField,
        TYPE_FLOAT:    forms.FloatField,
        TYPE_TIME:     forms.TimeField,
        TYPE_DATE:     forms.DateField,
        TYPE_DATETIME: forms.DateTimeField,
        TYPE_BOOLEAN:  forms.BooleanField,
    }
    
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), limit_choices_to=VALID_CUSTOM_CONTENT_TYPES)
    name = models.CharField(_('name'), max_length=100)
    label = models.CharField(_('label'), max_length=100)
    datatype = models.CharField(_('data type'), max_length=5, choices=DATATYPE_CHOICES)
    help_text = models.CharField(_('help text'), max_length=200, blank=True, null=True)
    required = models.BooleanField(_('required'), default=False)
    initial = models.CharField(_('initial'), max_length=200, blank=True, null=True)
    min_length = models.PositiveIntegerField(_('min length'), blank=True, null=True)
    max_length = models.PositiveIntegerField(_('max length'), blank=True, null=True)
    min_value = models.FloatField(_('min value'), blank=True, null=True)
    max_value = models.FloatField(_('max value'), blank=True, null=True)
    validator = PythonCodeField(_('validator'), blank=True, null=True, default=DEFAULT_VALIDATOR_VALUE)

    class Meta:
        verbose_name = _('custom field')
        verbose_name_plural = _('custom fields')

    #--------------------------------------------------------------------------
    def save(self):
        super(ContentTypeCustomField, self).save()
        # retrigger if we want to see the changes
        if not settings.DEBUG: force_reload()

    #--------------------------------------------------------------------------
    def get_form_widget(self):
        widget_type = ContentTypeCustomField.FIELD_TYPES[self.datatype]
        widget = widget_type(label=self.label,
                             help_text=self.help_text,
                             required=self.required)
        if self.datatype == ContentTypeCustomField.TYPE_TEXT:
            if self.min_length: widget.min_length = self.min_length
            widget.max_length = self.max_length if self.max_length else 200
            widget.widget = widgets.AdminTextInputWidget()     
        elif self.datatype == ContentTypeCustomField.TYPE_INTEGER:
            if self.min_value: widget.min_value = int(self.min_value)
            if self.max_value: widget.max_value = int(self.max_value)
        elif self.datatype == ContentTypeCustomField.TYPE_FLOAT:
            if self.min_value: widget.min_value = self.min_value
            if self.max_value: widget.max_value = self.max_value
        elif self.datatype == ContentTypeCustomField.TYPE_TIME:
            widget.widget = widgets.AdminTimeWidget()     
        elif self.datatype == ContentTypeCustomField.TYPE_DATE:
            widget.widget = widgets.AdminDateWidget()
        elif self.datatype == ContentTypeCustomField.TYPE_DATETIME:
            widget.widget = widgets.AdminSplitDateTime()
        elif self.datatype == ContentTypeCustomField.TYPE_BOOLEAN:
            pass
        return widget

    #--------------------------------------------------------------------------
    @staticmethod
    def get_fields_for_model(model):
        content_type = ContentType.objects.get_for_model(model)
        return ContentTypeCustomField.objects.filter(content_type=content_type)
    
    #--------------------------------------------------------------------------
    @staticmethod
    def get_fieldset_for_model(model, title=None):
        fields = ContentTypeCustomField.get_fields_for_model(model)
        if len(fields) > 0:
            return (title, { 'fields': [f.name for f in fields] })
        return None

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class ContentTypeCustomFieldValue(BaseModel):
    custom_field = models.ForeignKey(ContentTypeCustomField, verbose_name=_('custom field'))
    content_type = models.ForeignKey(ContentType, editable=False, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    value_text = models.TextField(blank=True, null=True)
    value_int = models.IntegerField(blank=True, null=True)
    value_float = models.FloatField(blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_time = models.TimeField(blank=True, null=True)
    value_datetime = models.DateTimeField(blank=True, null=True)
    value_bool = models.NullBooleanField(blank=True)

    def _get_value(self):
        return getattr(self, 'value_%s' % self.custom_field.datatype)
    def _set_value(self, new_value):
        setattr(self, 'value_%s' % self.custom_field.datatype, new_value)
    value = property(_get_value, _set_value)
    
    class Meta:
        verbose_name = _('custom field value')
        verbose_name_plural = _('custom field values')

    #--------------------------------------------------------------------------
    def save(self):
        # save content type as user shouldn't be able to change it
        self.content_type = self.custom_field.content_type
        super(ContentTypeCustomFieldValue, self).save()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.value)
