# -*- coding: utf-8 -*-

from django.conf import settings
from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin
#from civil.apps.custom.admin import customizable_admin

from .models import *


#==============================================================================
class ContributionTypeAdmin(BaseAdmin):
    list_display = ('id', 'name', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('created', 'modified')
    search_fields = ['name']

admin.site.register(ContributionType, ContributionTypeAdmin)


#==============================================================================
class SubscriptionTypeAdmin(BaseAdmin):
    list_display = ('id', 'name', 'is_active', 'contribution_type', 'period', 'length', 'length_type',
                    'from_day', 'from_month',  'to_day', 'to_month', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('contribution_type', 'length_type', 'is_active', 'created', 'modified')
    search_fields = ['name', 'description', 'contribution_type__name']
    fieldsets = [
        (None, {
            'fields': (
                ('name', 'is_active'),
                'description',
                'contribution_type',
                'minimum_cost',
                'period',
            )
        }),
        (None, {
            'fields': (
                ('length', 'length_type'),
            )
        }),
        (None, {
            'fields': (
                ('from_day', 'from_month'),
                ('to_day', 'to_month'),
            )
        }),
    ]

    class Media:
        js = (
            '%sadmin/js/subscriptiontype.js' % settings.STATIC_URL,
        )

admin.site.register(SubscriptionType, SubscriptionTypeAdmin)

#==============================================================================
class ContributionSubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    fieldsets = [
        (None, {
            'fields': (
                'contact',
                'type',
                'from_date',
                'to_date',
                'number',
                'source',
                'notes',
            )
        }),
    ]

class ContributionAdmin(BaseAdmin):
    list_display = ('id', 'contact', 'status', 'type', 'payment_type', 'amount', 'when', 'transaction', 'created', 'modified')
    list_display_links = ('id', 'contact', )
    list_filter = ('contact', 'status', 'type', 'payment_type', 'when', 'created', 'modified')
    search_fields = ['type__name', 'payment_type__name', 'transaction',
                     'contact__first_name', 'contact__last_name']
    inlines = [ContributionSubscriptionInline]

admin.site.register(Contribution, ContributionAdmin)


#==============================================================================
class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription

    def clean(self):
        cleaned_data = super(SubscriptionForm, self).clean()
        
        has_contribution = cleaned_data.get("has_contribution")
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")
        type = cleaned_data.get("type")
        contrib_type = cleaned_data.get("contrib_type")
        contrib_payment_type = cleaned_data.get("contrib_payment_type")
        contrib_amount = cleaned_data.get("contrib_amount")
        contrib_when = cleaned_data.get("contrib_when")

        if not to_date:
            cleaned_data["to_date"] = datetime.date(from_date.year,
                                                    type.to_month,
                                                    type.to_day)        

        # TODO - check if from_date is not > to_date

        if has_contribution:
            if not contrib_when:
                cleaned_data["contrib_when"] = from_date

            if not contrib_type:
                msg = _('Contribution type must be set')
                self._errors["contrib_type"] = self.error_class([msg])
                del cleaned_data["contrib_type"]
    
            if not contrib_payment_type:
                msg = _('Payment type must be set')
                self._errors["contrib_payment_type"] = self.error_class([msg])
                del cleaned_data["contrib_payment_type"]
                        
            if contrib_amount <= 0:
                msg = _('Amount cannot be less than or equal to zero')
                self._errors["contrib_amount"] = self.error_class([msg])
                del cleaned_data["contrib_amount"]

        # Always return the full collection of cleaned data.
        return cleaned_data


class SubscriptionAdmin(BaseAdmin):
    list_display = ('id', 'contact', 'type', 'status_text', 'source', 'from_date', 'to_date', 'number', 'has_contribution', 'created', 'modified')
    list_display_links = ('id', 'contact', )
    list_filter = ('contact', 'type', 'from_date', 'created', 'modified')
    search_fields = ['type__name', 'source', 'number', 'notes',
                     'contact__first_name', 'contact__last_name']
    readonly_fields = ('contrib_mail_sent',)
    fieldsets = [
        (None, {
            'fields': (
                'contact',
                'type',
                'from_date',
                'to_date',
                'number',
                'source',
                'notes',
                'has_contribution',
            )
        }),
        (_('Contribution'), {
            'fields': (
                'contrib_type',
                'contrib_payment_type',
                'contrib_amount',
                'contrib_when',
                'contrib_status',
                'contrib_transaction',
                ('contrib_send_receipt', 'contrib_mail_sent',)
            )
        }),
    ]
    form = SubscriptionForm

    #--------------------------------------------------------------------------
    def save_model(self, request, obj, form, change):
        super(SubscriptionAdmin, self).save_model(request, obj, form, change) 

    #--------------------------------------------------------------------------
    def delete_model(self, request, obj, form, change):
        super(SubscriptionAdmin, self).delete(request, obj, form, change) 

    #--------------------------------------------------------------------------
    class Media:
        js = (
            '%sadmin/js/subscription.js' % settings.STATIC_URL,
        )

admin.site.register(Subscription, SubscriptionAdmin)
