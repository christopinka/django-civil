# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.db.models import fields
from django.utils.translation import ugettext_lazy as _

from .fields import *


#==============================================================================
class RootModel(models.Model):
    class Meta:
        abstract = True


#==============================================================================
class TimeStampedModel(RootModel):
    """ 
    An abstract base class model that provides self-managed "created" and
    "modified" fields.
    """
    created = fields.DateTimeField(_('created'), auto_now_add=True)
    modified = fields.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


#==============================================================================
class BaseModel(TimeStampedModel):
    class Meta:
        abstract = True
