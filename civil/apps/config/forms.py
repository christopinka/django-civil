# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


#==============================================================================
class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.prefix = 'base'
        self.position = 'left'
        self.title = _('Base Form')
     

#==============================================================================
class GlobalConfigForm(BaseForm):
    SITE_NAME = forms.CharField(label=_('Site name'), max_length=50, initial='Django-CIVIL', required=True, 
                                help_text=_('Global site name visible in admin section'))

    DEBUG = forms.BooleanField(label=_('Debug'), initial=True, required=False, 
                               help_text=_('Site is running in debug mode'))

    def __init__(self, *args, **kwargs):
        super(GlobalConfigForm, self).__init__(*args, **kwargs)
        self.prefix = 'global'
        self.position = 'left'
        self.title = _('Global Configuration')


#==============================================================================
class UploadConfigForm(BaseForm):
    MAX_UPLOAD_SIZE = forms.IntegerField(label=_('Max upload size in bytes'), initial=10485760, required=True,
                                         help_text=_('Max upload size for files in the admin section'))

    def __init__(self, *args, **kwargs):
        super(UploadConfigForm, self).__init__(*args, **kwargs)
        self.prefix = 'upload'
        self.position = 'left'
        self.title = _('Upload Configuration')
