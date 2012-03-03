# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin
#from mptt.admin import MPTTModelAdmin

from .models import *

#==============================================================================
class ThemePlaceholderInline(admin.TabularInline):
    model = ThemePlaceholder
    extra = 0
    #classes = ('collapse open',)


class ThemeAdmin(BaseAdmin):
    list_display = ('thumbnail', 'id', 'name', 'slug', 'version', 'default', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('name', 'created', 'modified')
    search_fields = ['name', ]
    inlines = [ThemePlaceholderInline]
    
admin.site.register(Theme, ThemeAdmin)


#==============================================================================
class PluginPositionInline(admin.StackedInline):
    model = PluginPosition
    extra = 0
    filter_horizontal = ('included_pages', 'excluded_pages',)
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'show_name'),
                'status',
                'access',
                ('position', 'order'),
                'all_pages',
                'included_pages',
                'excluded_pages',
                'custom_html',
            )        
        }),
    )
    #classes = ('collapse open',)

class PluginAdmin(BaseAdmin):
    list_display = ('id', 'name', 'slug', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('name', 'created', 'modified')
    search_fields = ['name', ]
    inlines = [PluginPositionInline]
    
admin.site.register(Plugin, PluginAdmin)


#==============================================================================
class PageAdmin(BaseAdmin):
    list_display = ('id', 'name', 'slug', 'status', 'access', 'is_index', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('name', 'created', 'modified')
    search_fields = ['name', ]
    
admin.site.register(Page, PageAdmin)


#==============================================================================
class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    #classes = ('collapse open',)


class MenuAdmin(BaseAdmin):
    list_display = ('id', 'name', 'slug', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('name', 'created', 'modified')
    search_fields = ['name', ]
    inlines = [MenuItemInline]
    
admin.site.register(Menu, MenuAdmin)
