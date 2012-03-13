# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from civil.library.admin import BaseAdmin

from .models import *

#==============================================================================
class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 0
    #classes = ('collapse open',)
    
class VideoInline(admin.StackedInline):
    model = Video
    extra = 0
    #classes = ('collapse open',)

class AlbumAdmin(BaseAdmin):
    list_display = ('id', 'name', 'created', 'modified')
    list_display_links = ('id', 'name', )
    list_filter = ('created', 'modified')
    search_fields = ['name']
    inlines = [PhotoInline, VideoInline]

admin.site.register(Album, AlbumAdmin)


#==============================================================================
class PhotoAdmin(BaseAdmin):
    list_display = ('id', 'title', 'created', 'modified')
    list_display_links = ('id', 'title', )
    list_filter = ('created', 'modified')
    search_fields = ['title']

admin.site.register(Photo, PhotoAdmin)


#==============================================================================
class VideoAdmin(BaseAdmin):
    list_display = ('id', 'title', 'created', 'modified')
    list_display_links = ('id', 'title', )
    list_filter = ('created', 'modified')
    search_fields = ['title']

admin.site.register(Video, VideoAdmin)
