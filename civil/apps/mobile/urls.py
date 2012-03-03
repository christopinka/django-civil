# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView, DetailView, ListView

from civil.apps.base.models import Contact

import views

#==============================================================================
urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='home'),
    
    url(r'^about/', TemplateView.as_view(template_name="about.html")),
    url(r'^publishers/$', ListView.as_view(model=Contact)),
)
