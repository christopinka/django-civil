# -*- coding: utf-8 -*-

from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from civil.apps.search.models import SavedSearch


#==============================================================================
def save_search_action(description=_("Save search")):
    """
    """
    def save_search(modeladmin, request, queryset):
        SavedSearch.from_action(request, queryset)
        messages.success(request, _('Successfully saved search'))
        return HttpResponseRedirect(request.get_full_path())

    save_search.short_description = description
    return save_search
