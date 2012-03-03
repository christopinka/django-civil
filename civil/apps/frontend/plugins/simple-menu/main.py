# -*- coding: utf-8 -*-

from civil.apps.frontend.models import Page, Menu, MenuItem

class PluginClass(object):
    def render(self, page, position):
        #for item in MenuItem.objects.filter()
        template = ['<ul>']
        for p in Page.objects.filter(parent__isnull=True):
            template.append('<li><a href="/%s">%s</a></li>' % (p.slug, p.name))
        template.append('</ul>')
        return '\n'.join(template)
