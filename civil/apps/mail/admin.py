# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin

from civil.apps.base.models import *

from .models import *


#==============================================================================
admin.site.register(Signature, BaseAdmin)
admin.site.register(Attachments, BaseAdmin)


#==============================================================================
class OutboundServerAdmin(BaseAdmin):
    list_display = ('id', 'name', 'default', 'host', 'port', 'username', 'safe_password', 'timeout', 'created', 'modified')
    list_display_links = ('id', 'name', )
    save_as = True
    
admin.site.register(OutboundServer, OutboundServerAdmin)


#==============================================================================
class InboundServerAdmin(BaseAdmin):
    list_display = ('id', 'name', 'default', 'host', 'port', 'username', 'safe_password', 'timeout', 'created', 'modified')
    list_display_links = ('id', 'name', )
    save_as = True

admin.site.register(InboundServer, InboundServerAdmin)


#==============================================================================
class SenderEmailAdmin(BaseAdmin):
    list_display = ('id', 'name', 'default', 'email', 'created', 'modified')
    list_display_links = ('id', 'name', )
    save_as = True

admin.site.register(SenderEmail, SenderEmailAdmin)


#==============================================================================
class MailContactLogInline(admin.TabularInline):
    model = MailContactLog
    extra = 0
    max_num = 0
    fields = ('contact', 'sent', 'error')
    readonly_fields = ('contact', 'sent', 'error')
    #classes = ('collapse open',)

class MailLogAdmin(BaseAdmin):
    list_display = ('id', '__unicode__', 'when', 'finished', 'total', 'sent_mail_count', 'wrong_mail_count', 'created', 'modified')
    list_display_links = ('id', '__unicode__', )
    readonly_fields = ('instance', 'total', 'sent_mail_count', 'wrong_mail_count', 'when', 'error', 'finished',)
    inlines = [ MailContactLogInline, ]

    #--------------------------------------------------------------------------
    def resend_mail_action(self, request, obj = None):
        if obj and obj.instance:
            obj.instance.multiple_resend_email(obj)
    resend_mail_action.short_description=_('Resend wrong emails')

    change_buttons = [ resend_mail_action ]    
        
admin.site.register(MailLog, MailLogAdmin)


#==============================================================================
class IncludedScheduleInline(admin.TabularInline):
    model = MailLog
    extra = 0
    max_num = 0
    readonly_fields = ('total', 'error', 'finished')
    #classes = ('collapse open',)


class IncludedAttachmentsInline(admin.TabularInline):
    model = MailTemplate.attachments.through
    extra = 0
    #classes = ('collapse open',)


class MailTemplateForm(forms.ModelForm):
    #attachments = forms.ChoiceField() # keep this as it is in exclude
    server = forms.ModelChoiceField(queryset=OutboundServer.objects.all(),                                 
                                    initial=lambda: OutboundServer.get_default())
    reply_to = forms.ModelChoiceField(queryset=InboundServer.objects.all(),                                 
                                      initial=lambda: InboundServer.get_default())
    sender = forms.ModelChoiceField(queryset=SenderEmail.objects.all(),                                 
                                    initial=lambda: SenderEmail.get_default())
    
    class Meta:
        model = MailTemplate
        

class MailTemplateAdmin(BaseAdmin):
    list_display = ('id', 'name', 'action', 'default', 'subject', 'signature', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('sender', 'action', 'server',)
    search_fields = ['name', 'subject', 'html', 'text',]
    # exclude = ('attachments',) # this will broke the form
    fieldsets = (
        (None, {
            'fields': (
                'name',
                ('action', 'default'),
                ('server', 'sender', 'reply_to',),
                'subject',
                'html',
                'text',
                'signature',
            ),
        }),
        (None, {
            'fields': (
                'included_contacts',
                'excluded_contacts',
                'included_groups',
                'excluded_groups',
            ),
        }),
    )
    readonly_fields = ('attachments',)
    filter_horizontal = ('included_groups', 'excluded_groups', 'included_contacts', 'excluded_contacts',)
    inlines = [ IncludedAttachmentsInline, IncludedScheduleInline, ]
    form = MailTemplateForm
    save_as = True
    
    class Media:
        js = (
            '%sadmin/js/mailtemplate.js' % settings.STATIC_URL,
        )

    #---------------------------------------------------------------------------
    def queryset(self, request):
        # group by action (keeping null first)
        qs = super(MailTemplateAdmin, self).queryset(request)
        qs.query.group_by = ['action']
        return qs    

    #--------------------------------------------------------------------------
    def send_mail_action(self, request, obj = None):
        # TODO - this should be handled in a page of its own
        if obj:
            if obj.action is not None:
                messages.error(request, _('Cannot send predefined mail templates as mass mailing'))
            else:
                retval = obj.multiple_send_email()
                if retval:
                    messages.error(request, retval)
                else:
                    messages.info(request, _('Mails sent correctly'))
        return None
    send_mail_action.short_description=_('Send Mail')

    change_buttons = [ send_mail_action ]
    view_buttons = [ send_mail_action ]

admin.site.register(MailTemplate, MailTemplateAdmin)
