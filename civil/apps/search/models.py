# -*- coding: utf-8 -*-

import datetime
from django.conf import settings
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from civil.library.models import BaseModel


#==============================================================================
class SavedSearch(BaseModel):
    name = models.CharField(_('name'), max_length=100)
    path = models.CharField(_('path'), max_length=200)
    when = models.DateTimeField(_('when'), blank=True)
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = _('saved search')
        verbose_name_plural = _('saved searches')

    #--------------------------------------------------------------------------
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        if not self.id:
            self.when = datetime.datetime.now()
        super(SavedSearch, self).save()

    #--------------------------------------------------------------------------
    def test_link(self):
        return "<a href='%s'>Go To</a>" % (self.path)
    test_link.allow_tags = True

    #--------------------------------------------------------------------------
    @staticmethod
    def from_action(request, qs):
        ss = SavedSearch(path=request.get_full_path())
        ss.user = request.user
        ss.name = capfirst(u"%s" % qs.model._meta.verbose_name)
        ss.save()
        for item in qs:
            ssi = SavedSearchItem(search=ss)
            ssi.content_object = item
            ssi.save()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return u"%s - %s" % (self.when, self.name)


#==============================================================================
class SavedSearchItem(BaseModel):
    search = models.ForeignKey(SavedSearch)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('saved search item')
        verbose_name_plural = _('saved search items')

    def __unicode__(self):
        return self.search.name
