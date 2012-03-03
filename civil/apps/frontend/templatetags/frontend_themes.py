# -*- coding: utf-8 -*-

import os
from django.conf import settings
from django import template
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()

from civil.apps.frontend.models import Theme


#==============================================================================
class FrontendDefaultThemeNode(template.Node):
    def render(self, context):
        theme = Theme.get_default()
        theme_url = os.path.join(settings.MEDIA_URL, settings.THEMES_URL, theme.slug)
        if not theme_url.endswith('/'): theme_url = '%s/' % theme_url
        return theme_url
        
def frontend_default_theme_url(parser, token):
    return FrontendDefaultThemeNode()

register.tag('frontend_default_theme_url', frontend_default_theme_url)
