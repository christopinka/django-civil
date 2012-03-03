# -*- coding: utf-8 -*-

"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'civil.dashboard.CustomIndexDashboard'
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name

from civil.library.dashboard.savedsearch import SavedSearches
from civil.library.dashboard.simplelistmodels import SimpleModelList


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append a group for "Administration" & "Applications"
#        self.children.append(modules.Group(
#            _('Administration'),
#            column=1,
#            collapsible=True,
#            children = [
#                modules.AppList(
#                    _('Administration'),
#                    column=1,
#                    collapsible=False,
#                    models=('django.contrib.*',),
#                ),
#            ]
#        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            column=1,
            collapsible=True,
            css_classes=('collapse open',),
            exclude=('django.contrib.*',
                     'civil.apps.custom.*',
                     'civil.apps.definitions.*',
                     'civil.apps.search.*',
                     'civil.apps.social.*',
                     'tagging.*',),
        ))

        # append a group for "Administration"
        self.children.append(modules.Group(
            _('Administration'),
            column=1,
            collapsible=True,
            css_classes=('collapse closed',),
            children = [
                modules.AppList(
                    _('Administration'),
                    column=1,
                    collapsible=False,
                    models=('django.contrib.*',
                            'civil.apps.social.*',),
                ),
            ]
        ))

        # append an app list module for "Administration"
#        self.children.append(modules.ModelList(
#            _('Models Administration'),
#            column=1,
#            collapsible=True,
#            css_classes=('collapse closed',),
#            models=('django.contrib.*',),
#        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Media Management'),
            column=2,
            collapsible=True,
            css_classes=('collapse',),
            children=[
                {
                    'title': _('File Browser'),
                    'url': reverse('filebrowser:fb_browse'),
                    'external': False,
                },
                {
                    'title': _('Batch Import'),
                    'url': reverse('batchimport_import_home'),
                    'external': False,
                },
                {
                    'title': _('Site Settings'),
                    'url': reverse('config_show'),
                    'external': False,
                },
            ]
        ))

        # append a saved searches links
        self.children.append(SavedSearches(
            _('Saved Searches'),
            column=2,
            collapsible=True,
            css_classes=('collapse',),
            children=[]
        ))

        # append a group for "Tags"
        self.children.append(SimpleModelList(
            _('Tags'),
            column=2,
            collapsible=True,
            css_classes=('collapse closed',),
            models=('tagging.*',),
        ))

        # append a group for "Custom Fields"
        self.children.append(SimpleModelList(
            _('Custom fields'),
            column=2,
            collapsible=True,
            css_classes=('collapse closed',),
            models=('civil.apps.custom.*',),
        ))

        # append a simple model list for "Definitions"
        self.children.append(SimpleModelList(
            _('Definitions'),
            column=2,
            collapsible=True,
            css_classes=('collapse closed',),
            models=('civil.apps.definitions.*',),
        ))

        # append a backup / restore 
        if 'smuggler' in settings.INSTALLED_APPS:
            self.children.append(modules.LinkList(
                _('Backup / Restore'),
                column=2,
                collapsible=True,
                css_classes=('collapse closed',),
                children=[
                    {
                        'title': _('Backup database'),
                        'url': reverse('dump-data'),
                        'external': False,
                    },
                    {
                        'title': _('Restore database'),
                        'url': reverse('load-data'),
                        'external': False,
                    },
                ]
            ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            column=2,
            collapsible=True,
            css_classes=('collapse closed',),
            children=[
                {
                    'title': _('Django Documentation'),
                    'url': 'http://docs.djangoproject.com/',
                    'external': True,
                },
                {
                    'title': _('Grappelli Documentation'),
                    'url': 'http://packages.python.org/django-grappelli/',
                    'external': True,
                },
                {
                    'title': _('Grappelli Google-Code'),
                    'url': 'http://code.google.com/p/django-grappelli/',
                    'external': True,
                },
            ]
        ))

        # append a feed module (requires feedparser)
        #self.children.append(modules.Feed(
        #    _('Latest Django News'),
        #    column=2,
        #    feed_url='http://www.djangoproject.com/rss/weblog/',
        #    limit=5
        #))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))


