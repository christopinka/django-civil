# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from civil.library.models import BaseModel


#==============================================================================
class AddressType(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('address type')
        verbose_name_plural = _('address types')

    def __unicode__(self):
        return self.name


#==============================================================================
class PhoneType(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('phone type')
        verbose_name_plural = _('phone types')

    def __unicode__(self):
        return self.name

class PhoneKind(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('phone kind')
        verbose_name_plural = _('phone kinds')

    def __unicode__(self):
        return self.name


#==============================================================================
class EmailType(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('email type')
        verbose_name_plural = _('email types')

    def __unicode__(self):
        return self.name


#==============================================================================
class WebsiteType(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('website type')
        verbose_name_plural = _('website types')

    def __unicode__(self):
        return self.name


#==============================================================================
class RelationshipType(BaseModel):
    name = models.CharField(max_length=100)
    from_slug = models.CharField(max_length=100,
        help_text=_("Denote the relationship from the contact, i.e. 'following'"))
    to_slug = models.CharField(max_length=100,
        help_text=_("Denote the relationship to the contact, i.e. 'followers'"))
    symmetrical_slug = models.CharField(max_length=100, blank=True, null=True,
        help_text=_("When a mutual relationship exists, i.e. 'friends'"))

    class Meta:
        verbose_name = _('relationship type')
        verbose_name_plural = _('relationship types')

    def __unicode__(self):
        return self.from_slug

class ReverseRelationshipType(RelationshipType):
    class Meta:
        proxy = True
        verbose_name = _('relationship type')
        verbose_name_plural = _('relationship types')

    def __unicode__(self):
        return self.to_slug


#==============================================================================
class ContactType(BaseModel):
    name = models.CharField(_('name'), max_length=100)
    parent_type = models.ForeignKey('self', blank=True, null=True,
                                    related_name='child_type', verbose_name=_('parent'))

    class Meta:
        verbose_name = _('contact type')
        verbose_name_plural = _('contact types')

    def __unicode__(self):
        return self.name


#==============================================================================
class PrefixType(BaseModel):
    name = models.CharField(_('name'), max_length=100)
    verbose_name = models.CharField(_('verbose name'),max_length=100)

    class Meta:
        verbose_name = _('prefix type')
        verbose_name_plural = _('prefix types')

    def __unicode__(self):
        return self.name


#==============================================================================
class SuffixType(BaseModel):
    name = models.CharField(_('name'), max_length=100)
    verbose_name = models.CharField(_('verbose name'), max_length=100)

    class Meta:
        verbose_name = _('suffix type')
        verbose_name_plural = _('suffix types')

    def __unicode__(self):
        return self.name


#==============================================================================
class SexType(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('sex type')
        verbose_name_plural = _('sex types')

    def __unicode__(self):
        return self.name


#==============================================================================
class PaymentType(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('payment type')
        verbose_name_plural = _('payment types')

    def __unicode__(self):
        return self.name
