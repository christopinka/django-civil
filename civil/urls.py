# -*- coding: utf-8 -*-

import bootstrap

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url


#==============================================================================
urlpatterns = patterns('',)

#==============================================================================
urlpatterns = patterns('',
    url(r'^mobile/$', include('%s.apps.mobile.urls' % settings.PROJECT_DIRNAME)),
)

#==============================================================================
urlpatterns += patterns('',
    (r'^openid/', include('%s.apps.social.urls' % settings.PROJECT_DIRNAME)),
)

#==============================================================================
if 'grappelli' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^grappelli/', include('grappelli.urls')),
    )

if 'filebrowser' in settings.INSTALLED_APPS:
    from filebrowser.sites import site as filebrowser_site
    urlpatterns += patterns('',
        url(r'^admin/filebrowser/', include(filebrowser_site.urls)),
    )

#==============================================================================
if 'django.contrib.admindocs' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )

#==============================================================================
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    
    if 'smuggler' in settings.INSTALLED_APPS:
        urlpatterns += patterns('',
            url(r'^admin/', include('smuggler.urls')),
        )

    if 'livesettings' in settings.INSTALLED_APPS:
        urlpatterns += patterns('',
            url(r'^admin/settings/', include('livesettings.urls')),
        )

    urlpatterns += patterns('',
        url(r'^admin/batchimport/', include('%s.apps.batchimport.urls' % settings.PROJECT_DIRNAME)),
        url(r'^admin/config/', include('%s.apps.config.urls' % settings.PROJECT_DIRNAME)),
        url(r'^admin/', include(admin.site.urls)),
    )

#==============================================================================
if True: # settings.DEBUG or better settings.WEBSERVER_RUNNING
    static_url = settings.STATIC_URL
    if static_url.startswith('/'): static_url = static_url[1:]
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % static_url, 'django.views.static.serve',
            { 'document_root': settings.STATIC_ROOT, 'show_indexes': True }))
    
    media_url = settings.MEDIA_URL
    if media_url.startswith('/'): media_url = media_url[1:]
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % media_url, 'django.views.static.serve',
            { 'document_root': settings.MEDIA_ROOT, 'show_indexes': True }))

#==============================================================================
urlpatterns += patterns('',
    url(r'^', include('%s.apps.frontend.urls' % settings.PROJECT_DIRNAME)),
)

#==============================================================================
urlpatterns += patterns('',
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
)
