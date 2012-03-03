# -*- coding: utf-8 -*-

import operator
from django.db import models
from django.utils.encoding import smart_str
from django.core.exceptions import SuspiciousOperation
from django.contrib.admin.views.main import ALL_VAR, ORDER_VAR, \
                                            ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, \
                                            TO_FIELD_VAR, field_needs_distinct
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.contenttypes.models import ContentType

from civil.library.views.change_list import BaseChangeList

from .models import *


#==============================================================================
class CustomChangeList(BaseChangeList):

    def _get_additional_search_queries(self, bit, construct_search=lambda s: s):
        """
        Specify additional search queries lookup for use in search_fields,
        translating from custom fields searches to model lookup fields
        """
        content_type = ContentType.objects.get_for_model(self.model)
        custom = ContentTypeCustomField.objects.filter(content_type=content_type)
        or_queries = []
        for c in custom:
            query = models.Q(**{ 'custom_field': c, 'content_type': content_type, construct_search(str('value_text')): bit })
            found = ContentTypeCustomFieldValue.objects.filter(query)
            for f in found:
                or_queries.append(models.Q(**{ str(self.model._meta.pk.name): f.object_id }))
        return or_queries
        
    def get_query_set(self):
        """
        Subclass of the original get_query_set that allows searching in custom
        fields: translations from custom fields to model lookup fields is done
        in _get_additional_search_queries
        """
        use_distinct = False
        
        qs = self.root_query_set
        lookup_params = self.params.copy() # a dictionary of the query string
        for i in (ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, TO_FIELD_VAR):
            if i in lookup_params:
                del lookup_params[i]
        for key, value in lookup_params.items():
            if not isinstance(key, str):
                # 'key' will be used as a keyword argument later, so Python
                # requires it to be a string.
                del lookup_params[key]
                lookup_params[smart_str(key)] = value

            if not use_distinct:
                # Check if it's a relationship that might return more than one
                # instance
                field_name = key.split('__', 1)[0]
                try:
                    f = self.lookup_opts.get_field_by_name(field_name)[0]
                except models.FieldDoesNotExist:
                    raise IncorrectLookupParameters
                use_distinct = field_needs_distinct(f)

            # if key ends with __in, split parameter into separate values
            if key.endswith('__in'):
                value = value.split(',')
                lookup_params[key] = value

            # if key ends with __isnull, special case '' and false
            if key.endswith('__isnull'):
                if value.lower() in ('', 'false'):
                    value = False
                else:
                    value = True
                lookup_params[key] = value

            if not self.model_admin.lookup_allowed(key, value):
                raise SuspiciousOperation(
                    "Filtering by %s not allowed" % key
                )

        # Apply lookup parameters from the query string.
        try:
            qs = qs.filter(**lookup_params)
        # Naked except! Because we don't have any other way of validating "params".
        # They might be invalid if the keyword arguments are incorrect, or if the
        # values are not in the correct type, so we might get FieldError, ValueError,
        # ValicationError, or ? from a custom field that raises yet something else
        # when handed impossible data.
        except:
            raise IncorrectLookupParameters

        # Use select_related() if one of the list_display options is a field
        # with a relationship and the provided queryset doesn't already have
        # select_related defined.
        if not qs.query.select_related:
            if self.list_select_related:
                qs = qs.select_related()
            else:
                for field_name in self.list_display:
                    try:
                        f = self.lookup_opts.get_field(field_name)
                    except models.FieldDoesNotExist:
                        pass
                    else:
                        if isinstance(f.rel, models.ManyToOneRel):
                            qs = qs.select_related()
                            break

        # Set ordering.
        if self.order_field:
            qs = qs.order_by('%s%s' % ((self.order_type == 'desc' and '-' or ''), self.order_field))

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        if self.search_fields and self.query:
            orm_lookups = [construct_search(str(search_field))
                           for search_field in self.search_fields]
            for bit in self.query.split():
                or_queries = [models.Q(**{orm_lookup: bit})
                              for orm_lookup in orm_lookups]
                # XXX - start change
                or_queries += self._get_additional_search_queries(bit, construct_search)
                # XXX - end
                qs = qs.filter(reduce(operator.or_, or_queries))
            if not use_distinct:
                for search_spec in orm_lookups:
                    field_name = search_spec.split('__', 1)[0]
                    f = self.lookup_opts.get_field_by_name(field_name)[0]
                    if field_needs_distinct(f):
                        use_distinct = True
                        break

        if use_distinct:
            return qs.distinct()
        else:
            return qs
