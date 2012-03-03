# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin

from .models import *

#==============================================================================
class SavedSearchItemInline(admin.StackedInline):
    model = SavedSearchItem
    extra = 0
    classes = ('collapse closed',)


#==============================================================================
class SavedSearchAdmin(BaseAdmin):
    list_display = ('id', 'name', 'test_link',)
    list_display_links = ('id', 'name', )
    inlines = [ SavedSearchItemInline ]

    #--------------------------------------------------------------------------
    def queryset(self, request):
        """
            The queryset returned for this model admin
        """
        qs = super(SavedSearchAdmin, self).queryset(request)
        # superuser should see everything
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs

    #--------------------------------------------------------------------------
    def has_change_permission(self, request, obj=None):
        """
            Check also if we have the permissions to edit this object
        """
        has_class_permission = super(SavedSearchAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.user.id:
            return False
        return True

admin.site.register(SavedSearch, SavedSearchAdmin)
