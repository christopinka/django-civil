# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec, DateFieldFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from datetime import datetime

class ContactTypeFilterSpec(ChoicesFilterSpec):
    """
    Adds filtering by future and previous values in the admin
    filter sidebar. Set the is_live_filter filter in the model field attribute
    'is_live_filter'.    my_model_field.is_live_filter = True
    """

    def __init__(self, f, request, params, model, model_admin):
        from models import ContactType
        super(ContactTypeFilterSpec, self).__init__(f,
                                                    request,
                                                    params,
                                                    model,
                                                    model_admin)

        values_list = ContactType.objects.values_list(f.name, flat=True)
        self.lookup_choices = list(set(val[0] for val in values_list if val))

    def title(self):
        return self.field.verbose_name

# registering the filter
FilterSpec.filter_specs.insert(0,
  (lambda f: getattr(f, 'contact_type_filter', False), ContactTypeFilterSpec))
