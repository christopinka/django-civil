# -*- coding: utf-8 -*-

import os
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from civil.library.utils.reload import force_reload

from .forms import *
from .settings import CONFIG_FILE


#==============================================================================
def read_config():
    config_file = open(CONFIG_FILE, "r")
    data = simplejson.loads(config_file.read())
    config_file.close()
    return data

def write_config(data):
    config_file = open(CONFIG_FILE, 'w')
    config_file.write(simplejson.dumps(data))
    config_file.close()


#==============================================================================
def config_show(request, extra_context=None):
    """
    Manipulate the global configuration of the site
    """

    # recreate the config file if not existent
    if not os.path.exists(CONFIG_FILE):
        global_form = GlobalConfigForm()
        upload_form = UploadConfigForm()
        data = {}
        for f in global_form.fields:
            data[f] = global_form.fields[f].initial or None
        for f in upload_form.fields:
            data[f] = upload_form.fields[f].initial or None
        write_config(data)

    # read the config file data    
    data = read_config()
    
    if request.method == 'POST':
        # process the post
        global_form = GlobalConfigForm(request.POST)
        upload_form = UploadConfigForm(request.POST)
        
        if global_form.is_valid() and upload_form.is_valid():
            data = {}
            for f in global_form.fields:
                data[f] = global_form.cleaned_data[f]
            for f in upload_form.fields:
                data[f] = upload_form.cleaned_data[f]
            
            write_config(data)
            force_reload() # experimental
            
            messages.info(request, _('Settings file has been update successfully.'))
            return HttpResponseRedirect(reverse('config_show'))
        else:
            messages.error(request, _('Plase correct the errors below.'))
    else:
        # fill the form with the data
        global_form = GlobalConfigForm(initial=data)
        upload_form = UploadConfigForm(initial=data)

    forms = [
        global_form,
        upload_form
    ]   

    if extra_context is None:
        extra_context = {}

    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
        
    return render_to_response('config/config_show.html', 
                              { 'title': _('Edit configuration'),
                                'forms': forms },
                              context_instance=context)
