# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin
from civil.library.filter import *

from civil.apps.custom.admin import customizable_admin
from civil.apps.contribute.models import *

from .models import *


#==============================================================================
#admin.site.unregister(Site)

#admin.site.register(Address, BaseAdmin)
#admin.site.register(Phone, BaseAdmin)
#admin.site.register(Email, BaseAdmin)
#admin.site.register(Website, BaseAdmin)

#==============================================================================
class GroupAdmin(BaseAdmin):
    list_display = ('id', 'name', 'contact_count', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('name', 'created', 'modified')
    search_fields = ['name', ]

admin.site.register(Group, GroupAdmin)


#==============================================================================
class GroupInline(admin.StackedInline):
    model = Contact.groups.through
    extra = 0
    #classes = ('collapse open',)


#==============================================================================
class AddressInline(admin.StackedInline):
    model = Address
    extra = 0
    fieldsets = (
      (None, {
        'fields': (
            ('main', 'type', ),
            'address',
            ('city', 'cap',),
            'country',
            'location',
        ),
      }),
    )
    #classes = ('collapse open',)


#==============================================================================
class PhoneInline(admin.StackedInline):
    model = Phone
    extra = 0
    fieldsets = (
      (None, {
        'fields': (
            ('main', 'kind', 'type',),
            'number',
        ),
      }),
    )
    #classes = ('collapse open',)


#==============================================================================
class EmailInline(admin.StackedInline):
    model = Email
    extra = 0
    fieldsets = (
      (None, {
        'fields': (
            ('main', 'type',),
            'address',
        ),
      }),
    )
    #classes = ('collapse open',)


#==============================================================================
class RelationshipInline(admin.StackedInline):
    model = Relationship
    fk_name = 'from_contact'
    extra = 0
    fieldsets = (
      (None, {
        'fields': (
            ('type', 'to_contact', ),
        ),
      }),
    )
    #classes = ('collapse open',)


class ReverseRelationshipInline(admin.StackedInline):
    model = ReverseRelationship
    fk_name = 'to_contact'
    extra = 0
    fieldsets = (
      (None, {
        'fields': (
            ('type', 'from_contact', ),
        ),
      }),
    )
    #classes = ('collapse open',)

    def create_filtered_form(self, contact):
        class ReverseRelationshipForm(forms.ModelForm):
            type = forms.ModelChoiceField(label=_("relationship type"),
                queryset=ReverseRelationshipType.objects.all())
            from_contact = forms.ModelChoiceField(label=_("from contact"),
                queryset=Contact.objects.all())
            to_contact = forms.ModelChoiceField(label=_("to contact"),
                queryset=Contact.objects.filter(pk=contact.pk))
            class Meta:
                model = ReverseRelationship
        return ReverseRelationshipForm

    def get_formset(self, request, obj=None, **kwargs):
        if obj is not None:
            self.form = self.create_filtered_form(obj)
        return super(ReverseRelationshipInline, self).get_formset(request, obj, **kwargs)


#==============================================================================
class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    #classes = ('collapse open',)


#==============================================================================
class UserInline(admin.StackedInline):
    model = Contact.users.through
    extra = 0
    #classes = ('collapse open',)


#==============================================================================
class ContactAdmin(customizable_admin(Contact)):
    list_display = ('id', 'last_name', 'first_name', 'nickname', 'is_active', 'type', 'sex', 'birth_date', 'main_address', 'main_phone', 'main_email', 'group_list', 'created', 'modified')
    list_display_links = ('id', 'last_name', 'first_name', )
    list_filter = ('type', 'groups', 'created', 'modified')
    search_fields = ['last_name', 'first_name', 'nickname',
                     'addresses__address', 'addresses__city', 'addresses__cap',
                     'emails__address', 'websites__url', 'phones__number',
                     # this returns reverse relationships (search aku > lucio)
                     'relationships__last_name', 'relationships__first_name', 'relationships__nickname',
                     # this returns direct relationships (search lucio > aku)
                     #'relations__last_name', 'relations__first_name', 'relations__nickname',
                     'groups__name', 'subscription__number']
    fieldsets = [
        (None, {
            'fields': (
                'is_active',
                ('prefix', 'nickname',),
                ('first_name', 'second_name'),
                'last_name',
                'type',
                'sex',
                'birth_date',
                ('decease_date', 'deceased',)
            )
        }),
        (None, {
            'fields': ('notes',)
        }),
        (None, {
            'fields': (('dont_call', 'dont_sms', 'dont_mail', 'dont_post',),)
        }),
    ]
    inlines = [ GroupInline,
                PhoneInline,
                EmailInline,
                AddressInline,
                SubscriptionInline,
                RelationshipInline,
                ReverseRelationshipInline,
                UserInline ]
    exclude = ('groups', 'users',)

    #---------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super(ContactAdmin, self).__init__(*args, **kwargs)

    #---------------------------------------------------------------------------
    def get_form(self, request, obj=None, **kwargs):
        """
            Returns a specific form for this admin
        """
        # modify visualization for certain users
        if not request.user.is_superuser:
            #self.exclude.append('field_to_hide')
            #self.inlines.remove(UserInline)
            pass
        form = super(ContactAdmin, self).get_form(request, obj, **kwargs)
        return form

    #---------------------------------------------------------------------------
    def queryset(self, request):
        """
            The queryset returned for this model admin
        """
        qs = super(ContactAdmin, self).queryset(request)
        #qs = qs.filter(Q(is_staff=True) | Q(is_superuser=True))
        return qs

    #--------------------------------------------------------------------------
    def has_change_permission(self, request, obj=None):
        """
            Check also if we have the permissions to edit this object
        """
        has_permission = super(ContactAdmin, self).has_change_permission(request, obj)
        #if obj is not None and not request.user.is_superuser and request.user.id != obj.user.id:
        return has_permission

admin.site.register(Contact, ContactAdmin)
