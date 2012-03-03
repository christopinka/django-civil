# -*- coding: utf-8 -*-

from django.contrib.admin.actions import delete_selected
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _


#==============================================================================
def delete_all_action(description=_("Delete all records")):

    def delete_all(modeladmin, request, queryset):
        if not modeladmin.has_delete_permission(request):
            raise PermissionDenied
        return delete_selected(modeladmin, request, modeladmin.model.objects.all())
    
    delete_all.short_description = description
    return delete_all
    