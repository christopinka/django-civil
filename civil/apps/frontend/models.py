# -*- coding: utf-8 -*-

import io, os, shutil, zipfile, tempfile, datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson

from civil.library.models import BaseModel
from civil.library.fields import autoslug
from civil.library.fields import html as ckfields
from civil.library.decorators import unique_boolean, autoconnect

from mptt.models import MPTTModel, TreeForeignKey


#==============================================================================
THEMES_URL = getattr(settings, 'THEMES_URL', 'themes/')
PLUGIN_PATH = 'plugins/'
DEFAULT_TMP_PREFIX = 'civil'


#==============================================================================
STATUS_DRAFT = 1
STATUS_PUBLISHED = 2
STATUS_DELETED = 3
STATUS_CHOICES = (
    (STATUS_DRAFT, _('Draft')),
    (STATUS_PUBLISHED, _('Published')),
    (STATUS_DELETED, _('Deleted')),
)

ACCESS_PUBLIC = 1
ACCESS_RESTRICTED = 2
ACCESS_PUBLIC_ONLY = 3
ACCESS_CHOICES = (
    (ACCESS_PUBLIC, _('Public')),
    (ACCESS_RESTRICTED, _('Restricted')),
    (ACCESS_PUBLIC_ONLY, _('Public only')),
)


#==============================================================================
class ThemePlaceholder(BaseModel):
    theme = models.ForeignKey('Theme', verbose_name=_('theme'))
    name = models.CharField(_('name'), max_length=200)

    class Meta:
        verbose_name = _('theme placeholder')
        verbose_name_plural = _('theme placeholders')

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.theme.slug)


@autoconnect
class Theme(BaseModel):
    name = models.CharField(_('name'), max_length=200)
    slug = autoslug.AutoSlugField(prepopulate_from=['name'])
    version = models.FloatField(_('version'), default=0.1)
    default = models.BooleanField(_('default'))

    class Meta:
        verbose_name = _('theme')
        verbose_name_plural = _('themes')

    #--------------------------------------------------------------------------
    @unique_boolean('default')
    def save(self):
        """
            Overridden save to allow the default to be unique
        """
        super(Theme, self).save()

    #--------------------------------------------------------------------------
    def pre_delete(self):
        """
            Removes any traces of the theme directory
        """
        finaldir = os.path.join(settings.MEDIA_ROOT, THEMES_URL, self.slug)
        shutil.rmtree(finaldir)

    #--------------------------------------------------------------------------
    def thumbnail(self):
        thumb_url = os.path.join(THEMES_URL, self.slug, 'thumbnail.png')
        thumb = os.path.join(settings.MEDIA_ROOT, thumb_url)
        if os.path.exists(thumb):
            return "<img src='%s' style='width:220px' />" % os.path.join(settings.MEDIA_URL, thumb_url)
        else:
            return "&nbsp;"
    thumbnail.allow_tags = True

    #--------------------------------------------------------------------------
    @staticmethod
    def install_from_zip(filebytes):
        destdir = tempfile.mkdtemp(prefix=DEFAULT_TMP_PREFIX)
        
        finaldir = os.path.join(settings.MEDIA_ROOT, THEMES_URL)
        
        try:
            zf = zipfile.ZipFile(io.BytesIO(filebytes))
            zf.extractall(destdir)
            
            fp = open(os.path.join(destdir, "info.json"), "r")
            obj = simplejson.loads(fp.read())
            fp.close()
            
            name = obj.get('name')
            slug = obj.get('slug')
            version = obj.get('version')

            # TODO - check slug existance
            # TODO - check versions and upgrade
            
            themedir = os.path.join(finaldir, slug)
            if os.path.exists(themedir) or Theme.objects.filter(slug=slug).count() == 1:
                # TODO - raise
                print "A theme with the same slug already exists !"
            else:
                theme = Theme(name=name, slug=slug, version=version)
                theme.save()

                for p in obj.get('positions', []):
                    ph = ThemePlaceholder(theme=theme, name=p)
                    ph.save()
                
                os.makedirs(themedir)
                for f in obj.get('files', []):
                    if f.startswith('/'): f = f[1:]

                    split = f.split('/')
                    if len(split) > 1:
                        d = themedir
                        for s in split[:-1]:
                            d = os.path.join(d, s)
                            if not os.path.exists(d):
                                os.makedirs(d)

                    srcpath = os.path.join(destdir, f)
                    dstpath = os.path.join(themedir, f)
                    shutil.copy(srcpath, dstpath)
            
        except zipfile.BadZipfile:
            print "bad zip file" # TODO - remove
        # remove temporary directory   
        shutil.rmtree(destdir)

    #--------------------------------------------------------------------------
    @staticmethod
    def get_default():
        return Theme.objects.get(default=True)

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
@autoconnect
class Plugin(BaseModel):
    name = models.CharField(_('name'), max_length=200)
    slug = autoslug.AutoSlugField(prepopulate_from=['name'])
    version = models.FloatField(_('version'), default=0.1)

    #--------------------------------------------------------------------------
    def pre_delete(self):
        """
            Removes any traces of the plugin directory
        """
        finaldir = os.path.join(os.path.dirname(__file__), PLUGIN_PATH, self.slug)
        shutil.rmtree(finaldir)

    #--------------------------------------------------------------------------
    def load(self):
        import importlib
        module = importlib.import_module('%s.apps.frontend.plugins.%s.main' % (settings.PROJECT_DIRNAME, self.slug))
        reload(module) # TODO - useless
        return module

    #--------------------------------------------------------------------------
    @staticmethod
    def install_from_zip(filebytes):
        destdir = tempfile.mkdtemp(prefix=DEFAULT_TMP_PREFIX)
        finaldir = os.path.join(os.path.dirname(__file__), PLUGIN_PATH)
        try:
            zf = zipfile.ZipFile(io.BytesIO(filebytes))
            zf.extractall(destdir)
            
            # TODO - check if info.json exists !            
            
            fp = open(os.path.join(destdir, "info.json"), "r")
            obj = simplejson.loads(fp.read())
            fp.close()
            
            name = obj.get('name')
            slug = obj.get('slug')
            version = obj.get('version')
            
            # TODO - check slug existance
            # TODO - check versions and upgrade
            
            plugindir = os.path.join(finaldir, slug)
            if os.path.exists(plugindir) or Plugin.objects.filter(slug=slug).count() == 1:
                # TODO - raise
                print "A plugin with the same slug already exists !"
            else:
                plugin = Plugin(name=name, slug=slug, version=version)
                plugin.save()
                
                os.makedirs(plugindir)
                for f in obj.get('files', []):
                    if f.startswith('/'): f = f[1:]

                    split = f.split('/')
                    if len(split) > 1:
                        d = plugindir
                        for s in split[:-1]:
                            d = os.path.join(d, s)
                            if not os.path.exists(d):
                                os.makedirs(d)

                    srcpath = os.path.join(destdir, f)
                    dstpath = os.path.join(plugindir, f)
                    shutil.copy(srcpath, dstpath)

            #plugin = __import__('civil.apps.frontend.plugins.%s.main' % slug)
            #print plugin
        except zipfile.BadZipfile:
            print "bad zip file" # TODO - remove
        # remove temporary directory   
        shutil.rmtree(destdir)
        # TODO - test syncdb ?
        from django.core.management import call_command 
        call_command('syncdb') 

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class PluginPosition(BaseModel):
    name = models.CharField(_('name'), max_length=200)
    show_name = models.BooleanField(_('show name'))
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=STATUS_DRAFT)
    access = models.IntegerField(_('access'), choices=ACCESS_CHOICES, default=ACCESS_PUBLIC)
    plugin = models.ForeignKey('Plugin', verbose_name=_('plugin'))
    position = models.ForeignKey('ThemePlaceholder', verbose_name=_('position'), blank=True, null=True)
    order = models.IntegerField(_('order'), default=1)
    included_pages = models.ManyToManyField('Page', related_name='included_pages',
                                            blank=True, null=True,
                                            verbose_name=_('included pages'))
    excluded_pages = models.ManyToManyField('Page', related_name='excluded_pages',
                                            blank=True, null=True,
                                            verbose_name=_('excluded pages'))
    all_pages = models.BooleanField(_('all pages'))
    
    custom_html = ckfields.HTMLField(_('custom html'), blank=True, null=True)
    custom_value = models.CharField(_('custom value'), max_length=200, blank=True, null=True)

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s: %s at %s" % (self.name, self.position, self.order)


#==============================================================================
class Page(MPTTModel, BaseModel):
    name = models.CharField(_('name'), max_length=200)
    slug = autoslug.AutoSlugField(prepopulate_from=['name'])
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=STATUS_DRAFT)
    access = models.IntegerField(_('access'), choices=ACCESS_CHOICES, default=ACCESS_PUBLIC)
    author = models.ForeignKey(User, verbose_name=_('author'))

    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent page'))

    # TODO - language

    title = models.CharField(_('title'), max_length=200, blank=True, null=True)
    subtitle = models.CharField(_('subtitle'), max_length=200, blank=True, null=True)
    keywords = models.TextField(_('keywords'), blank=True, null=True, help_text=_("If omitted, the keywords will be the same as the article tags."))
    description = models.TextField(_('description'), blank=True, null=True, help_text=_("If omitted, the description will be determined by the first bit of the article's content."))

    excerpt = ckfields.HTMLField(_('excerpt'), blank=True, null=True)
    content = ckfields.HTMLField(_('content'), blank=True, null=True)

    #followup_for = models.ManyToManyField('self', symmetrical=False, blank=True, help_text=_('Select any other articles that this article follows up on.'), related_name='followups')
    #related_articles = models.ManyToManyField('self', blank=True)

    publish_date = models.DateTimeField(_('publish date'), default=datetime.datetime.now, help_text=_('The date and time this article shall appear online.'))
    expiration_date = models.DateTimeField(_('expiration date'), blank=True, null=True, help_text=_('Leave blank if the article does not expire.'))
    
    is_index = models.BooleanField(_('is index'))

    #--------------------------------------------------------------------------
    @unique_boolean('is_index')
    def save(self):
        """
            Overridden save to allow the is_index to be unique
        """
        super(Page, self).save()

    #--------------------------------------------------------------------------
    def get_absolute_url(self):
        return "/%s/" % self.slug

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)


#==============================================================================
class MenuItem(MPTTModel, BaseModel):
    name = models.CharField(_('name'), max_length=200)
    slug = autoslug.AutoSlugField(prepopulate_from=['name'])
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=STATUS_DRAFT)
    access = models.IntegerField(_('access'), choices=ACCESS_CHOICES, default=ACCESS_PUBLIC)
    menu = models.ForeignKey('Menu', verbose_name=_('menu'))
    page = models.ForeignKey('Page', verbose_name=_('page'))
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', verbose_name=_('parent menu item'))

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)


class Menu(BaseModel):
    name = models.CharField(_('name'), max_length=200)
    slug = autoslug.AutoSlugField(prepopulate_from=['name'])
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=STATUS_DRAFT)
    access = models.IntegerField(_('access'), choices=ACCESS_CHOICES, default=ACCESS_PUBLIC)

    #--------------------------------------------------------------------------
    def __unicode__(self):
        return "%s" % (self.name)
