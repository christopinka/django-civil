# -*- coding: utf-8 -*-

import datetime
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import Template, Context

from civil.library.models import BaseModel
from civil.library.decorators import unique_boolean, unique_boolean_for_instance
from civil.library.fields import html as ckfields

from civil.apps.definitions.models import *
from civil.apps.base.models import *

from filebrowser import fields as fbfields

from .send import send_mail


#==============================================================================
class OutboundServer(BaseModel):
    """
        Model that specify a smtp server to use for sending
    """
    name = models.CharField(_('name'), max_length=200)
    host = models.CharField(_('host'), max_length=200)
    port = models.PositiveIntegerField(_('port'), default=25, blank=True, null=True)
    username = models.CharField(_('username'), max_length=200, blank=True, null=True)
    password = models.CharField(_('password'), max_length=200, blank=True, null=True)
    timeout = models.PositiveIntegerField(_('timeout'), default=120)
    default = models.BooleanField(_('default'))

    class Meta:
        verbose_name = _('outbound server')
        verbose_name_plural = _('outbound servers')

    #--------------------------------------------------------------------------
    @unique_boolean('default')
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        super(OutboundServer, self).save()

    #--------------------------------------------------------------------------
    def safe_password(self):
        """
            Useful safe protector for password in list_views
        """
        return '*' * len(self.password) 
    safe_password.short_description = _("password")

    #--------------------------------------------------------------------------
    def connect(self):
        """
            Connect to the specified smtp server
        """
        import smtplib
        smtp = smtplib.SMTP(timeout=self.timeout)
        if self.port:
            smtp.connect(self.host, int(self.port))
        else:
            smtp.connect(self.host)
        if self.username and self.password:
            smtp.login(self.username, self.password)
        return smtp

    #--------------------------------------------------------------------------
    @staticmethod
    def get_default():
        return OutboundServer.objects.get(default=True)

    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class InboundServer(BaseModel):
    """
        Model that specify a pop3 address for handling bounce messages
    """
    name = models.CharField(_('name'), max_length=200)
    email = models.EmailField(max_length=200, verbose_name=_('email'))
    host = models.CharField(_('host'), max_length=200)
    port = models.PositiveIntegerField(_('port'), default=110, blank=True, null=True)
    username = models.CharField(_('username'), max_length=200, blank=True, null=True)
    password = models.CharField(_('password'), max_length=200, blank=True, null=True)
    timeout = models.PositiveIntegerField(_('timeout'), default=120)
    default = models.BooleanField(_('default'))

    class Meta:
        verbose_name = _('inbound server')
        verbose_name_plural = _('inbound servers')

    #--------------------------------------------------------------------------
    @unique_boolean('default')
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        super(InboundServer, self).save()

    #--------------------------------------------------------------------------
    def safe_password(self):
        """
            Useful safe protector for password in list_views
        """
        return '*' * len(self.password) 
    safe_password.short_description = _("password")

    #--------------------------------------------------------------------------
    def connect(self):
        """
            Connect to the specified smtp server
        """
        import poplib
        if self.port:
            pop3 = poplib.POP3(self.host, port=self.port, timeout=self.timeout)
        else:
            pop3 = poplib.POP3(self.host, timeout=self.timeout)
        pop3.user(self.username)
        pop3.pass_(self.password)
        return pop3
    
    #--------------------------------------------------------------------------
    def list_messages(self):
        """
            Parse messages
        """
        pop3 = self.connect()
        messages = []
        for i in range(len(pop3.list()[1])):
            for j in pop3.retr(i+1)[1]:
                messages.append(j)
                print j # TODO - remove
        return messages

    #--------------------------------------------------------------------------
    @staticmethod
    def get_default():
        return InboundServer.objects.get(default=True)

    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class SenderEmail(BaseModel):
    """
        Model that specify a sender address for the newsletter
    """
    name = models.CharField(_('name'), max_length=200)
    email = models.EmailField(max_length=200, verbose_name=_('email'))
    default = models.BooleanField(_('default'))

    class Meta:
        verbose_name = _('sender')
        verbose_name_plural = _('senders')

    #--------------------------------------------------------------------------
    @unique_boolean('default')
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        super(SenderEmail, self).save()

    #--------------------------------------------------------------------------
    @staticmethod
    def get_default():
        return SenderEmail.objects.filter(default=True)

    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class Signature(BaseModel):
    """
        Model that specify a signature for the newsletter
    """
    name = models.CharField(_('name'), max_length=200)
    html = ckfields.HTMLField(_('html'))
    text = models.TextField(_('text'))
    default = models.BooleanField(_('default'))

    class Meta:
        verbose_name = _('signature')
        verbose_name_plural = _('signatures')

    #--------------------------------------------------------------------------
    @unique_boolean('default')
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        super(Signature, self).save()

    #--------------------------------------------------------------------------
    @staticmethod
    def get_default():
        return Signature.objects.get(default=True)

    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class Attachments(BaseModel):
    """
        Model that specify an attachment for a newsletter
    """
    file = fbfields.FileBrowseField(_("file"), max_length=200)

    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')

    def __unicode__(self):
        return "%s" % (self.file)


#==============================================================================
class MailTemplate(BaseModel):
    """
        Model that holds a mail subject, body, sender, list of receivers
    """
    ACTION_REPLY = 1
    ACTION_WELCOME = 2
    ACTION_SUBSCRIBE = 3   
    ACTION_UNSUBSCRIBE = 4
    ACTION_RESUBSCRIBE = 5
    ACTION_OPTOUT = 6
    ACTION_RECEIPT = 7
    ACTION_CHOICES = (
        (ACTION_REPLY, _('Reply')),
        (ACTION_WELCOME, _('Welcome')),
        (ACTION_SUBSCRIBE, _('Subscribe')),
        (ACTION_UNSUBSCRIBE, _('Unsubscribe')),
        (ACTION_RESUBSCRIBE, _('Resubscribe')),
        (ACTION_OPTOUT, _('Opt-out')),
        (ACTION_RECEIPT, _('Receipt')),
    )

    name = models.CharField(_('name'), max_length=200)
    default = models.BooleanField(_('default'))
    action = models.IntegerField(_('action'), choices=ACTION_CHOICES, blank=True, null=True)
    server = models.ForeignKey(OutboundServer, verbose_name=_('server'))
    sender = models.ForeignKey(SenderEmail, related_name='sender', verbose_name=_('sender'))
    reply_to = models.ForeignKey(InboundServer, related_name='reply_to',
                                  blank=True, null=True,
                                  verbose_name=_('reply to'))
    subject = models.CharField(_('subject'), max_length=200)
    html = ckfields.HTMLField(_('html'))
    text = models.TextField(_('text'))
    signature = models.ForeignKey(Signature, blank=True, null=True, verbose_name=_('signature'))
    included_contacts = models.ManyToManyField(Contact, related_name='included_contacts',
                                               blank=True, null=True,
                                               verbose_name=_('included contacts'))
    excluded_contacts = models.ManyToManyField(Contact, related_name='excluded_contacts',
                                               blank=True, null=True,
                                               verbose_name=_('excluded contacts'))
    included_groups = models.ManyToManyField(Group, related_name='included_groups',
                                             blank=True, null=True,
                                             verbose_name=_('included groups'))
    excluded_groups = models.ManyToManyField(Group, related_name='excluded_groups',
                                             blank=True, null=True,
                                             verbose_name=_('excluded groups'))
    attachments = models.ManyToManyField(Attachments, related_name='attachments',
                                         blank=True, null=True,
                                         verbose_name=_('attachments'))

    class Meta:
        verbose_name = _('mail template')
        verbose_name_plural = _('mail templates')

    #--------------------------------------------------------------------------
    @unique_boolean_for_instance('default', 'action')
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        super(MailTemplate, self).save()

    #--------------------------------------------------------------------------
    def collect_contacts(self):
        """
            Collect the contacts choosen for this instance, pushing included
            groups and contacts and excluding the selected ones. The returned
            list of Contact users will be unique (no duplicates contacts)
        """
        contacts = set()
        # included
        for g in self.included_groups.all():
            for c in g.get_contacts():
                if not c.dont_mail: # avoid user that are unregistered to mail
                    contacts.add(c)
        for c in self.included_contacts.all():
            if not c.dont_mail:  # avoid user that are unregistered to mail
                contacts.add(c)
        # excluded
        for g in self.excluded_groups.all():
            for c in g.get_contacts():
                if c in contacts:
                    contacts.remove(c)
        for c in self.excluded_contacts.all():
            if c in contacts:
                contacts.remove(c)
        return list(contacts)

    #--------------------------------------------------------------------------
    def get_sender(self):
        return "%s <%s>" % (self.sender.name, self.sender.email)

    #--------------------------------------------------------------------------
    def get_reply_to(self):
        return self.reply_to.email if self.reply_to else None

    #--------------------------------------------------------------------------
    def get_body_html(self):
        """
            Return the body in html format
        """
        html = ['<html>',
                '<head>',
                '<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">',
                '</head>',
                '<body>',
                self.html,
                self.signature.html if self.signature else '',
                '</body>',
                '</html>']
        # TODO - handle predefined sender signature
        return '\n'.join(html)
        
    #--------------------------------------------------------------------------
    def get_body_text(self):
        """
            Return the body in text format
        """
        text = [self.text,
                self.signature.text if self.signature else '']
        # TODO - handle predefined sender signature
        return '\n'.join(text)

    #--------------------------------------------------------------------------
    def single_send_email(self, contact, obj = None):
        """
            Send the email to a single contact
        """
        # create the log
        log = MailLog(instance=self)
        log.count = 1
        log.save()
        # connect to smtp
        smtp = self.server.connect()
        # prepare the template / adding signature
        hb = Template(self.get_body_html())
        tb = Template(self.get_body_text())
        # send email
        sentlog = MailContactLog(log=log, contact=contact)
        sentlog.save()
        # get the destination email
        email = contact.main_email()
        if not email:
            sentlog.error = _('The contact does not have a defined email address')
            sentlog.save()
            return sentlog.error
        destination = "%s %s <%s>" % (contact.first_name, contact.last_name, email)
        # render the template
        ctx = Context({ 'contact': contact, 'obj': obj })
        htmlbody = hb.render(ctx)
        textbody = tb.render(ctx)
        # send emails
        try:
            send_mail(smtp,
                      self.get_sender(),
                      destination,
                      self.subject,
                      htmlbody,
                      textbody,
                      self.attachments.all(),
                      self.get_reply_to())
            mail_sent = True
            mail_error = None
        except:
            mail_sent = False
            mail_error = sys.exc_info()[0]
        # save schedule logs
        if mail_error: sentlog.error = mail_error
        sentlog.sent = mail_sent
        sentlog.save()
        # update schedule finishing
        log.finished = True
        log.save()
        # None is ok        
        return mail_error

    #--------------------------------------------------------------------------
    def multiple_send_email(self):
        """
            Send the email to multiple contacts
        """
        # collect contacts
        contacts = self.collect_contacts()
        # create the log
        log = MailLog(instance=self)
        log.count = len(contacts)
        log.save()
        if len(contacts) == 0:
            log.error = _('No contacts have been selected or found')
            log.save()
            return log.error
        # connect to smtp
        smtp = self.server.connect()
        # prepare the template / adding signature
        hb = Template(self.get_body_html())
        tb = Template(self.get_body_text())
        # send email
        for c in contacts:
            sentlog = MailContactLog(log=log, contact=c)
            sentlog.save()
            # get the destination email
            email = c.main_email()
            if not email:
                sentlog.error = _('The contact does not have a defined email address')
                sentlog.save()
                continue
            destination = "%s %s <%s>" % (c.first_name, c.last_name, email)
            # render the template
            ctx = Context({ 'contact': c, })
            htmlbody = hb.render(ctx)
            textbody = tb.render(ctx)
            # send emails
            try:
                send_mail(smtp,
                          self.get_sender(),
                          destination,
                          self.subject,
                          htmlbody,
                          textbody,
                          self.attachments.all(),
                          self.get_reply_to())
                mail_sent = True
                mail_error = None
            except:
                mail_sent = False
                mail_error = sys.exc_info()[0]
            # save schedule logs
            if mail_error: sentlog.error = mail_error
            sentlog.sent = mail_sent
            sentlog.save()
        # update schedule finishing
        log.finished = True
        log.save()
        # None is ok        
        return None

    #--------------------------------------------------------------------------
    def multiple_resend_email(self, log):
        # connect to smtp
        smtp = self.server.connect()
        # prepare the template / adding signature
        hb = Template(self.get_body_html())
        tb = Template(self.get_body_text())                       
        # iterate on wrong sent emails
        notsent = MailContactLog.objects.filter(log=log, sent=False)
        for sentlog in notsent:
            c = sentlog.contact
            # get the destination email
            email = c.main_email()
            if not email:
                sentlog.error = _('The contact does not have a defined email address')
                sentlog.save()
                continue
            destination = "%s %s <%s>" % (c.first_name, c.last_name, email)
            # render the template
            ctx = Context({ 'contact': c, })
            htmlbody = hb.render(ctx)
            textbody = tb.render(ctx)
            # send emails
            try:
                send_mail(smtp,
                          self.get_sender(),
                          destination,
                          self.subject,
                          htmlbody,
                          textbody,
                          self.attachments.all(),
                          self.get_reply_to())
                mail_sent = True
                mail_error = None
                log.count += 1
            except:
                mail_sent = False
            # save schedule logs
            if mail_error: sentlog.error = mail_error
            sentlog.sent = mail_sent
            sentlog.save()
        # update schedule finishing
        log.save()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class MailLog(BaseModel):
    """
        A specific mail that has been sent somewhen
    """
    instance = models.ForeignKey(MailTemplate, verbose_name=_('instance'))
    total = models.PositiveIntegerField(_('total'), default=0)
    when = models.DateTimeField(_('when'), blank=True)
    error = models.TextField(_('error'), blank=True, null=True)
    finished = models.BooleanField(_('finished'), default=False)
    log = models.ManyToManyField(Contact, through='MailContactLog',
                                 related_name='log', verbose_name=_('log'))

    class Meta:
        verbose_name = _('mail log')
        verbose_name_plural = _('mail logs')

    #--------------------------------------------------------------------------
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        self.total = MailContactLog.objects.filter(log=self).count()
        if not self.id and not self.when:
            self.when = datetime.datetime.now()
        super(MailLog, self).save()

    #--------------------------------------------------------------------------
    def sent_mail_count(self):
        return MailContactLog.objects.filter(log=self, sent=True).count()

    #--------------------------------------------------------------------------
    def wrong_mail_count(self):
        return MailContactLog.objects.filter(log=self, sent=False).count()

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.instance.name)


#==============================================================================
class MailContactLog(BaseModel):
    """
        Model that holds a log of sent mails to each contact.
    """
    log = models.ForeignKey(MailLog, verbose_name=_('log'))
    contact = models.ForeignKey(Contact, verbose_name=_('contact'))
    when = models.DateTimeField(_('when'), blank=True)
    error = models.TextField(_('error'), blank=True, null=True)
    sent = models.BooleanField(_('sent'), default=False)

    class Meta:
        verbose_name = _('mail contact log')
        verbose_name_plural = _('mail contact logs')

    #--------------------------------------------------------------------------
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        if not self.id and not self.when:
            self.when = datetime.datetime.now()
        super(MailContactLog, self).save()
