# -*- coding: utf-8 -*-

class PluginClass(object):
    def render(self, page, position):
        return '<h1>{{ page.title }}</h1><hr>'
