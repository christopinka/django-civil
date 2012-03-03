# -*- coding: utf-8 -*-

from django import forms
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType

from civil.library.utils.reload import force_reload
from civil.library.fields.code import PythonCodeField

from .models import ContentTypeCustomField, ContentTypeCustomFieldValue


#==============================================================================
def customizable_form(clazz):
    """
        Returns a customizable form field for ContenTypeCustomFields
    """

    def customizable_form_metaclass(clazz):
        """
            Create a metaclass for the model form
        """
        class CustomFieldModelFormMetaclass(forms.ModelForm.__metaclass__): 
            def __new__(cls, name, bases, attrs):
                fields = ContentTypeCustomField.get_fields_for_model(clazz)
                a = attrs.copy()
                for f in fields:
                    a[str(f.name)] = forms.Field()
                return super(CustomFieldModelFormMetaclass, cls).__new__(cls, name, bases, a)

        return CustomFieldModelFormMetaclass

    
    class CustomFieldModelForm(forms.ModelForm):
        __metaclass__ = customizable_form_metaclass(clazz)
        
        def __init__(self, *args, **kwargs):
            super(CustomFieldModelForm, self).__init__(*args, **kwargs)
            content_type = ContentType.objects.get_for_model(self._meta.model)
            fields = ContentTypeCustomField.objects.filter(content_type=content_type)
            self.instance = kwargs.get('instance', None)
            for f in fields:
                name = str(f.name)
                self.fields[name] = f.get_form_widget()
                self.fields[name].required = f.required
                initial = f.initial
                if self.instance:
                    value = ContentTypeCustomFieldValue.objects.filter(custom_field=f,
                                                                       content_type=content_type,
                                                                       object_id=self.instance.id)
                    if len(value) > 0:
                        initial = value[0].value
                self.fields[name].initial = initial
                self.initial[name] = initial
    
        def clean(self):
            cleaned_data = super(CustomFieldModelForm, self).clean()
            content_type = ContentType.objects.get_for_model(self._meta.model)
            fields = ContentTypeCustomField.objects.filter(content_type=content_type)
            for f in fields:
                name = str(f.name)
                value = cleaned_data[name]
                if f.validator:
                    func = PythonCodeField.evaluate(f.validator).get('validator', None)
                    if func:
                        try:
                            func(value, self.instance)
                        except Exception, arg:
                            self._errors[name] = self.error_class([unicode(arg)])
                            del cleaned_data[name]
            print cleaned_data
            return cleaned_data    
        
        def save(self, commit=True):
            instance = super(CustomFieldModelForm, self).save(commit=False)
            instance.save()
            self.save_m2m()
            content_type = ContentType.objects.get_for_model(self._meta.model)
            fields = ContentTypeCustomField.objects.filter(content_type=content_type)
            for f in fields:
                name = str(f.name)
                fv = ContentTypeCustomFieldValue.objects.filter(custom_field=f,
                                                                content_type=content_type,
                                                                object_id=instance.id)
                if len(fv) > 0:
                    value = fv[0]
                    value.value = self.cleaned_data[name]
                else:
                    value = ContentTypeCustomFieldValue(custom_field=f,
                                                        object_id=instance.id,
                                                        value=self.cleaned_data[name])
                value.save()
            return instance
       
        class Meta:
            model = clazz
    
    return CustomFieldModelForm
