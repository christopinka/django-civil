# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from .views import *

#==============================================================================
urlpatterns = patterns('',
    #url(r'^config_show/$', config_show, name='config_show'),
    url(r'^', config_show, name='config_show'),
)
