# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from civil.library.models import BaseModel
from civil.library.fields import country, location
from civil.library.decorators import autoconnect

from civil.apps.custom.manager import CustomizableModelManager
from civil.apps.definitions.models import *


#==============================================================================
class ContactUser(models.Model): # simple through model
    contact = models.ForeignKey('Contact')
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "%s (%s)" % (self.user.username, self.user.email)


#==============================================================================
class ContactGroup(models.Model): # simple through model
    contact = models.ForeignKey('Contact')
    group = models.ForeignKey('Group')

    def __unicode__(self):
        return self.group.__unicode__()


class Group(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def get_contacts(self):
        return Contact.objects.filter(groups__pk__in=[self.pk])

    def contact_count(self):
        return Contact.objects.filter(groups__pk__in=[self.pk]).count()

    def __unicode__(self):
        return self.name


#==============================================================================
class Address(BaseModel):
    type = models.ForeignKey(AddressType, verbose_name=_('address type'))
    main = models.BooleanField(_('main address'))
    address = models.CharField(_('address'), max_length=200, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    cap = models.CharField(_('cap'), max_length=20, blank=True, null=True)
    country = country.CountryField(_('country'), blank=True, null=True)
    is_billing = models.BooleanField(_('is billing'))
    contact = models.ForeignKey('Contact', related_name='addresses', verbose_name=_('contact'))
    location = location.LocationField(_('location'))

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
    
    #--------------------------------------------------------------------------
    def save(self):
        if settings.CONNECTION_AVAILABLE and self.address:
            address = "%s, %s %s %s" % (self.address, self.cap, self.city, self.country)
            self.location = Address.geocode(address)
        super(Address, self).save()

    #--------------------------------------------------------------------------
    @staticmethod    
    def geocode(address):
        import urllib
        params = urllib.urlencode({'q': address, 'output': 'csv', 'key': settings.GOOGLE_API_KEY, 'oe': 'utf8'})
        request = "http://maps.google.com/maps/geo?%s" % params
        data = urllib.urlopen(request).read()
        dlist = data.split(',')
        if dlist[0] == '200':
            return "%s,%s" % (dlist[2], dlist[3])
        else:
            return None

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s %s %s" % (self.address, self.cap, self.city)


#==============================================================================
class Phone(BaseModel):
    number = models.CharField(_('number'), max_length=20)
    main = models.BooleanField(_('main phone'))
    kind = models.ForeignKey(PhoneKind, verbose_name=_('phone kind'))
    type = models.ForeignKey(PhoneType, verbose_name=_('phone type'))
    contact = models.ForeignKey('Contact', related_name='phones', verbose_name=_('contact'))

    class Meta:
        verbose_name = _('phone')
        verbose_name_plural = _('phones')

    def __unicode__(self):
        return self.number


#==============================================================================
class Email(BaseModel):
    address = models.EmailField(_('address'), max_length=200, unique=True)
    main = models.BooleanField(_('main email'))
    type = models.ForeignKey(EmailType, verbose_name=_('email type'))
    contact = models.ForeignKey('Contact', related_name='emails', verbose_name=_('contact'))

    class Meta:
        verbose_name = _('email')
        verbose_name_plural = _('emails')

    def __unicode__(self):
        return self.address


#==============================================================================
class Website(BaseModel):
    url = models.URLField(_('url'))
    type = models.ForeignKey(WebsiteType, verbose_name=_('website type'))
    contact = models.ForeignKey('Contact', related_name='websites', verbose_name=_('contact'))

    class Meta:
        verbose_name = _('website')
        verbose_name_plural = _('websites')

    def __unicode__(self):
        return self.url


#==============================================================================
class Relationship(BaseModel):
    type = models.ForeignKey(RelationshipType, verbose_name=_('relationship type'))
    from_contact = models.ForeignKey('Contact', related_name='from_contact', verbose_name=_('from contact'))
    to_contact = models.ForeignKey('Contact', related_name='to_contact', verbose_name=_('to contact'))

    class Meta:
        unique_together = (('from_contact', 'to_contact', 'type'),)
        verbose_name = _('relationship')
        verbose_name_plural = _('relationships')

    def __unicode__(self):
        return "%s %s %s" % (self.type.from_slug,
                             self.to_contact.last_name,
                             self.to_contact.first_name)

class ReverseRelationship(Relationship):
    class Meta:
        proxy = True
        verbose_name = _('reverse relationship')
        verbose_name_plural = _('reverse relationships')

    def __unicode__(self):
        return "%s %s %s" % (self.type.to_slug,
                             self.from_contact.last_name,
                             self.from_contact.first_name)


#==============================================================================
@autoconnect
class Contact(BaseModel):
    """
        An abstract base class model that provides self-managed "created" and
        "modified" fields.
    """
    first_name = models.CharField(_('first name'), max_length=100)
    second_name = models.CharField(_('second name'), max_length=100, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=100)
    nickname = models.CharField(_('nickname'), max_length=100, blank=True, null=True)
    prefix = models.ForeignKey(PrefixType, blank=True, null=True, verbose_name=_('prefix'))
    suffix = models.ForeignKey(SuffixType, blank=True, null=True, verbose_name=_('suffix'))

    type = models.ForeignKey(ContactType, blank=True, null=True, verbose_name=_('contact type'))

    sex = models.ForeignKey(SexType, blank=True, null=True, verbose_name=_('sex'))
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    deceased = models.BooleanField(_('deceased'), default=False)
    decease_date = models.DateField(_('decease date'), blank=True, null=True)

    is_active = models.BooleanField(_('is active'), default=True)

    # TODO - are these really necessary ?
    default_email = models.EmailField(_('email'), max_length=200, blank=True, null=True)
    default_phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    
    dont_call = models.BooleanField(_('don\'t call'), default=False)
    dont_sms = models.BooleanField(_('don\'t sms'), default=False)
    dont_mail = models.BooleanField(_('don\'t mail'), default=False)
    dont_post = models.BooleanField(_('don\'t post'), default=False)

    notes = models.TextField(_('notes'), blank=True, null=True)

    # TODO - how to handle inlines correctly
    #addresses = models.ManyToManyField(Address, through='ContactAddress', related_name='addresses', verbose_name=_('addresses'))
    #phones = models.ManyToManyField(Phone, through='ContactPhone', related_name='phones', verbose_name=_('phones'))
    #emails = models.ManyToManyField(Email, through='ContactEmail', related_name='emails', verbose_name=_('emails'))
    #websites = models.ManyToManyField(Website, through='ContactWebsite', related_name='websites', verbose_name=_('websites'))

    groups = models.ManyToManyField(Group, through='ContactGroup', related_name='groups', verbose_name=_('groups'))
    users = models.ManyToManyField(User, through='ContactUser', related_name='users', verbose_name=_('users'))
    relations = models.ManyToManyField('Contact', through='Relationship', related_name='relationships', verbose_name=_('relations'))
    # TODO - rename relations=relationships and relationships=reverse_relationships

    objects = CustomizableModelManager()

    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

    #--------------------------------------------------------------------------
    def m2m_changed(self):
        # update the main addresses and phones
        self.default_email = self.main_email()
        self.default_phone = self.main_phone()
        self.save()

    #--------------------------------------------------------------------------
    def main_address(self):
        objects = self.addresses.all()
        if len(objects):
            for o in objects:
                if o.main == True: return o.__unicode__()
            return objects[0].__unicode__()
        return None

    #--------------------------------------------------------------------------
    def main_phone(self):
        objects = self.phones.all()
        if len(objects):
            for o in objects:
                if o.main == True: return o.__unicode__()
            return objects[0].__unicode__()
        return None

    #--------------------------------------------------------------------------
    def main_email(self):
        objects = self.emails.all()
        if len(objects):
            for o in objects:
                if o.main == True: return o.__unicode__()
            return objects[0].__unicode__()
        return None

    #--------------------------------------------------------------------------
    def group_list(self):
        objects = self.groups.all()
        if len(objects):
            return ', '.join(sorted([o.group.name for o in objects]))
        return None

    #--------------------------------------------------------------------------
    def users_list(self):
        objects = self.users.all()
        if len(objects):
            return ', '.join(sorted([o.user.name for o in objects]))
        return None

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s %s" % (self.last_name, self.first_name)


#==============================================================================
# Diconnect the create_superuser signal
from django.db.models import signals
from django.contrib.auth.management import create_superuser
from django.contrib.auth import models as auth_app

signals.post_syncdb.disconnect(
    create_superuser,
    sender = auth_app,
    dispatch_uid = "django.contrib.auth.management.create_superuser")
