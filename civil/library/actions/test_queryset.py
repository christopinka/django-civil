# -*- coding: utf-8 -*-

from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

#==============================================================================
def test_queryset_action(description=_("Testing queryset")):
    """
    """
    def test_queryset(modeladmin, request, queryset):
        print request.get_full_path()
        print queryset.model
        print queryset
        # TODO
        # save a queryset
        #    - create new name
        #    - save url
        #    - save user
        # for each obj in queryset
        #    - content type
        #    - save id
        response = HttpResponse(mimetype='text/plain')
        return response

    test_queryset.short_description = description
    return test_queryset
