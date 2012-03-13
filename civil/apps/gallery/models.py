# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from civil.library.models import BaseModel


#==============================================================================
class Album(BaseModel):
    name = models.CharField(_('name'), max_length=100)
    summary = models.TextField(_('summary'))
    
    class Meta:
        verbose_name = _('album')
        verbose_name_plural = _('albums')

    #--------------------------------------------------------------------------
    def save(self):
        super(Album, self).save()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class Photo(BaseModel):
    title = models.CharField(_('title'), max_length=256)
    summary = models.TextField(_('summary'), blank=True, null=True)
    image = models.ImageField(_('image'), upload_to='photos/%Y/%m')
    album = models.ForeignKey(Album, verbose_name=_('album'))
    is_cover_photo = models.BooleanField(_('is_cover_photo'))

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')

    #--------------------------------------------------------------------------
    def save(self):
        super(Photo, self).save()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.title)


#==============================================================================
class Video(BaseModel):
    title = models.CharField(_('title'), max_length=256)
    summary = models.TextField(_('summary'), blank=True, null=True)
    youtube_code = models.CharField(_('youtube code'), max_length=50)
    album = models.ForeignKey(Album, verbose_name=_('album'))
    is_cover_video = models.BooleanField(_('is_cover_video'))

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')

    #--------------------------------------------------------------------------
    def save(self):
        super(Video, self).save()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.title)
    
