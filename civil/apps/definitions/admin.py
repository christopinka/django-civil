# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin

from .models import *

#==============================================================================
class NameOnlyAdmin(BaseAdmin):
    list_display = ('id', 'name', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('created', 'modified')
    search_fields = ['name']

#==============================================================================
admin.site.register(AddressType, NameOnlyAdmin)
admin.site.register(PhoneType, NameOnlyAdmin)
admin.site.register(EmailType, NameOnlyAdmin)
admin.site.register(WebsiteType, NameOnlyAdmin)
admin.site.register(SexType, NameOnlyAdmin)
admin.site.register(RelationshipType, NameOnlyAdmin)
admin.site.register(PaymentType, NameOnlyAdmin)

#==============================================================================
admin.site.register(ContactType, BaseAdmin)
admin.site.register(PrefixType, BaseAdmin)
admin.site.register(SuffixType, BaseAdmin)
