# -*- coding: utf-8 -*-

import time, datetime
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from civil.library.models import BaseModel

from civil.apps.base.models import Contact
from civil.apps.definitions.models import PaymentType
from civil.apps.mail.models import MailTemplate


#==============================================================================
class ContributionType(BaseModel):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('contribution type')
        verbose_name_plural = _('contribution types')

    def __unicode__(self):
        return self.name


#==============================================================================
class SubscriptionType(BaseModel):

    PERIODIC_FIXED = 1
    PERIODIC_LENGTH = 2
    PERIODIC_CHOICES = (
        (PERIODIC_FIXED, _('Fixed start')),
        (PERIODIC_LENGTH, _('Fixed length')),
    )

    LENGTH_DAYS = 1
    LENGTH_WEEKS = 2
    LENGTH_MONTHS = 3
    LENGTH_YEARS = 4
    LENGTH_CHOICES = (
        (LENGTH_DAYS, _('Days')),
        (LENGTH_WEEKS, _('Weeks')),
        (LENGTH_MONTHS, _('Months')),
        (LENGTH_YEARS, _('Years')),
    )

    MONTHS_CHOICES = tuple((m, time.strftime('%b', time.strptime(str(m), '%m'))) for m in xrange(1, 13))
    DAYS_CHOICES = tuple((d, str(d)) for d in xrange(1, 32))
    
    name = models.CharField(_('name'), max_length=100)
    description = models.CharField(_('description'), max_length=200, blank=True, null=True)
    minimum_cost = models.DecimalField(max_digits=30, decimal_places=2, verbose_name=_('minimum cost'), default=0.00)
    contribution_type = models.ForeignKey(ContributionType, verbose_name=_('contribution type'))
    length = models.PositiveIntegerField(_('length'), default=1)
    length_type = models.PositiveIntegerField(_('length type'), choices=LENGTH_CHOICES, default=LENGTH_YEARS)
    period = models.PositiveIntegerField(_('period'), choices=PERIODIC_CHOICES, default=PERIODIC_FIXED)
    from_month = models.PositiveIntegerField(_('from month'), choices=MONTHS_CHOICES, default=1)
    from_day = models.PositiveIntegerField(_('from day'), choices=DAYS_CHOICES, default=1)
    to_month = models.PositiveIntegerField(_('to month'), choices=MONTHS_CHOICES, default=12)
    to_day = models.PositiveIntegerField(_('to day'), choices=DAYS_CHOICES, default=31)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # TODO - invio mail promemoria scadenza ?
    # TODO - gestione modelli di messaggio ?

    class Meta:
        verbose_name = _('subscription type')
        verbose_name_plural = _('subscription types')

    def __unicode__(self):
        return self.name


#==============================================================================
class Contribution(BaseModel):

    STATUS_DONE = 1
    STATUS_WAITING = 2
    STATUS_FAILED = 3
    STATUS_CANCELLED = 4
    STATUS_CHOICES = (
        (STATUS_DONE, _('Completed')),
        (STATUS_WAITING, _('Waiting')),
        (STATUS_FAILED, _('Failed')),
        (STATUS_CANCELLED, _('Cancelled')),
    )
    
    contact = models.ForeignKey(Contact, verbose_name=_('contact'))
    type = models.ForeignKey(ContributionType, verbose_name=_('type'))
    payment_type = models.ForeignKey(PaymentType, verbose_name=_('payment type'))
    amount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name=_('amount'), default=0.00)
    when = models.DateField(_('when'), default=datetime.date.today)
    status = models.PositiveIntegerField(_('status'), choices=STATUS_CHOICES, default=STATUS_DONE)
    transaction = models.CharField(_('transaction'), max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = _('contribution')
        verbose_name_plural = _('contributions')

    #--------------------------------------------------------------------------
    def save(self):
        super(Contribution, self).save()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return self.type.name
        

#==============================================================================
class Subscription(BaseModel):
    
    STATUS_FUTURE = 1
    STATUS_CURRENT = 2
    STATUS_EXPIRED = 3
    STATUS_CHOICES = (
        (STATUS_FUTURE, _('Future')),
        (STATUS_CURRENT, _('Current')),
        (STATUS_EXPIRED, _('Expired')),
    )
    
    contact = models.ForeignKey(Contact, verbose_name=_('contact'))
    type = models.ForeignKey(SubscriptionType, verbose_name=_('type'))
    from_date = models.DateField(_('from date'), default=datetime.date.today)
    to_date = models.DateField(_('to date'), blank=True, null=True) # should take type into account
    number = models.CharField(_('number'), max_length=100, blank=True, null=True)
    source = models.CharField(_('source'), max_length=100, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    has_contribution = models.BooleanField(_('has contribution'), default=False)

    # this fields should update the contribution stuff
    contrib_type = models.ForeignKey(ContributionType, verbose_name=_('type'), blank=True, null=True)
    contrib_payment_type = models.ForeignKey(PaymentType, verbose_name=_('payment type'), blank=True, null=True)
    contrib_amount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name=_('amount'), default=0.00, blank=True, null=True)
    contrib_when = models.DateField(_('when'), blank=True, null=True)
    contrib_status = models.PositiveIntegerField(_('status'), choices=Contribution.STATUS_CHOICES, default=Contribution.STATUS_DONE, blank=True, null=True)
    contrib_transaction = models.CharField(_('transaction'), max_length=200, blank=True, null=True)
    contrib_send_receipt = models.BooleanField(_('send receipt'), default=False)
    contrib_mail_sent = models.BooleanField(_('mail sent'), default=False, editable=False)

    contribution = models.ForeignKey(Contribution, related_name='contribution', verbose_name=_('contribution'), blank=True, null=True)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    #--------------------------------------------------------------------------
    def save(self):
        if self.has_contribution:
            contrib = self.contribution
            if not contrib:
                contrib = Contribution()
            contrib.contact = self.contact
            contrib.type = self.contrib_type
            contrib.payment_type = self.contrib_payment_type
            contrib.amount = self.contrib_amount
            contrib.when = self.contrib_when
            contrib.status = self.contrib_status
            contrib.transaction = self.contrib_transaction
            contrib.save()
            self.contribution = contrib

            # send receipt to the contact
            if self.contrib_send_receipt:
                self.contrib_send_receipt = False
                mail = MailTemplate.objects.get(action=MailTemplate.ACTION_RECEIPT, default=True)
                retval = mail.single_send_email(self.contact, contrib)
                if not retval:
                    self.contrib_mail_sent = True
        else:
            if self.contribution:
                self.contribution.delete()
                self.contribution = None
        super(Subscription, self).save()

    #--------------------------------------------------------------------------
    def status(self):
        today = datetime.date.today()
        if today < self.from_date:
            return Subscription.STATUS_FUTURE
        elif today >= self.from_date and today <= self.to_date:
            return Subscription.STATUS_CURRENT
        return Subscription.STATUS_EXPIRED

    #--------------------------------------------------------------------------
    def status_text(self):
        return Subscription.STATUS_CHOICES[self.status() - 1][1]

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return u"%s: %s from %s to %s" % (self.status_text(),
                                          self.type.name,
                                          self.from_date,
                                          self.to_date,)
