# -*- coding: utf-8 -*-

from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType

from .models import ContentTypeCustomField, ContentTypeCustomFieldValue


#==============================================================================
class CustomizableModelManager(Manager):
    """
    This manager allows searching in custom fields specified for a model
    """

    def filter(self, *args, **kwargs):
        qs = self.get_query_set().filter(*args)
        for lookup, value in kwargs.items():
            lookups = self._filter_by_lookup(qs, lookup, value)
            qs = qs.filter(**lookups)
        return qs

    def exclude(self, *args, **kw):
        qs = self.get_query_set().exclude(*args)
        for lookup, value in kw.items():
            lookups = self._filter_by_lookup(qs, lookup, value)
            qs = qs.exclude(**lookups)
        return qs

    def _filter_by_lookup(self, qs, lookup, value):
        content_type = ContentType.objects.get_for_model(self.model)
        fields   = self.model._meta.get_all_field_names()
        custom = dict((s.name, s) for s in ContentTypeCustomField.objects.filter(content_type=content_type))
        if '__' in lookup:
            name, sublookup = lookup.split('__', 1)
        else:
            name, sublookup = lookup, None
        if name == 'pk':
            name = self.model._meta.pk.name
        if name in fields:
            return { lookup: value }
        elif name in custom:
            attr = custom.get(name)
            value_lookup = 'value_text'
            if sublookup:
                value_lookup = '%s__%s' % (value_lookup, sublookup)
            found = ContentTypeCustomFieldValue.objects.filter(**{ 'custom_field': attr,
                                                                   'content_type': content_type,
                                                                   value_lookup: value})
            ids = [f.object_id for f in found]
            if len(ids) > 0:
                return {
                    str('%s__in' % (self.model._meta.pk.name)): ids
                }
            else:
                return {
                    str('%s__in' % (self.model._meta.pk.name)): []
                }

        raise NameError('Cannot filter items by attributes: unknown '
                        'attribute "%s". Available fields: %s. '
                        'Available custom fields: %s.' % (name,
                        ', '.join(fields), ', '.join(custom)))                   
