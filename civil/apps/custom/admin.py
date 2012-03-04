# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin

from .forms import customizable_form
from .models import ContentTypeCustomField, ContentTypeCustomFieldValue
from .change_list import CustomChangeList


#==============================================================================
def customizable_admin(cls):
    """
    Returns a customizable admin class
    """

    class CustomSearchableAdmin(BaseAdmin):
        form = customizable_form(cls)

        def __init__(self, *args, **kwargs):
            super(CustomSearchableAdmin, self).__init__(*args, **kwargs)
            # add the custom fields to the fieldsets (if present)
            # @see customizable_form and ContentTypeCustomField
            if self.fieldsets:
                if isinstance(self.fieldsets, tuple):
                    self.fieldsets = list(self.fieldsets)
                fieldset = ContentTypeCustomField.get_fieldset_for_model(self.form._meta.model)
                if fieldset: self.fieldsets.append(fieldset)

        def get_form(self, request, obj=None, **kwargs):
            ## modify visualization for certain users
            #if not request.user.is_superuser:
            #    self.exclude.append('field_to_hide')
            #    self.inlines.remove(UserInline)
            #    pass
            form = super(CustomSearchableAdmin, self).get_form(request, obj, **kwargs)
            return form

        def get_changelist(self, request, **kwargs):
            return CustomChangeList

        def queryset(self, request):
            qs = super(CustomSearchableAdmin, self).queryset(request)
            #qs = qs.filter(Q(is_staff=True) | Q(is_superuser=True))
            return qs

        def has_change_permission(self, request, obj=None):
            has_permission = super(CustomSearchableAdmin, self).has_change_permission(request, obj)
            #if obj is not None and not request.user.is_superuser and request.user.id != obj.user.id:
            return has_permission

    return CustomSearchableAdmin


#==============================================================================
class ContentTypeCustomFieldAdmin(BaseAdmin):
    list_display = ('id', 'name', 'label', 'datatype', 'required', 'initial', 'help_text', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('datatype', 'required', 'created', 'modified')
    search_fields = ['name', 'label', 'help_text', 'initial', 'created']
    fieldsets = [
        (None, {
            'fields': (
                'name',
                ('datatype', 'required'),
                'label', 'help_text',
                'initial',
            )
        }),
        (None, {
            'fields': (
                'content_type',
            )
        }),
        (None, {
            'fields': (
                ('min_length', 'max_length'),
            )
        }),
        (None, {
            'fields': (
                ('min_value', 'max_value'),
            )
        }),
        (None, {
            'fields': (
                'validator',
            )
        }),
    ]

    class Media:
        js = (
            '%sadmin/js/contenttypecustomfield.js' % settings.STATIC_URL,
        )

admin.site.register(ContentTypeCustomField, ContentTypeCustomFieldAdmin)


#==============================================================================
class ContentTypeCustomFieldValueAdmin(BaseAdmin):
    list_display = ('id', 'custom_field', 'content_type', 'object_id', 'content_object', 'value', 'created', 'modified')
    list_display_links = ('id', 'custom_field', )
    list_filter = ('custom_field', 'content_type', 'created', 'modified')
    search_fields = ['custom_field__name', 'custom_field__label', 'content_type__name',
                     'value_text', 'value_int', 'value_float', 'value_date', 'value_time', 'value_dtm', 'value_bool',]

admin.site.register(ContentTypeCustomFieldValue, ContentTypeCustomFieldValueAdmin)
