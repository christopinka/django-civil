# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^$', views.display_index, name='index'),
    url(r'^login/$', views.login_view, name='login_view'),
    url(r'^logout/$', views.logout_view, name='logout_view'),

    url(r'^(?P<slug>[\w_-]+)/$', views.display_page_by_slug, name='page_by_slug'),
    url(r'^page/(?P<id>\d+)/$', views.display_page_by_id, name='page_by_id'),
)
