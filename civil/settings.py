# -*- coding: utf-8 -*-

import os, sys, socket
import bootstrap
_ = lambda s : s

#=================================================================================
from apps.config import get_config

#=================================================================================
# Check internet connection (slow on some lans!)
try:
    if socket.gethostbyname('www.google.it') != None:
        CONNECTION_AVAILABLE = True
except (socket.gaierror, socket.timeout):
    CONNECTION_AVAILABLE = False

#==============================================================================
# Full filesystem path to the project.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Name of the directory for the project.
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]

BASE_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
THIRDPARTY_PATH = os.path.normpath(os.path.join(BASE_PATH, "thirdparty"))
APPS_PATH = os.path.normpath(os.path.join(BASE_PATH, "apps"))
DATABASE_PATH = os.path.normpath(os.path.join(BASE_PATH, "database"))

#==============================================================================
DEBUG = get_config('DEBUG', True) # True
TEMPLATE_DEBUG = DEBUG

#==============================================================================
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

#==============================================================================
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h1#6usb!oh$-2a*x=!cw5tccmc^#@n!(j80n$-gzmka(e4i@%#'

#==============================================================================
# Google api key for (http://127.0.0.1:8000)
GOOGLE_API_KEY = 'ABQIAAAAQZhl5nWApCa87L99-gySihTpH3CbXHjuCVmaTc5MkkU4wO1RRhSY63qY5SSW26er0uYr_q9abUV7hg'

#==============================================================================
# Site identification and name
SITE_ID = 1
SITE_NAME = get_config('SITE_NAME', 'Django-CIVIL')

#==============================================================================
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME':     os.path.join(DATABASE_PATH, 'default.sqlite'), # Or path to database file if using sqlite3.
        'USER':     '',                           # Not used with sqlite3.
        'PASSWORD': '',                           # Not used with sqlite3.
        'HOST':     '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT':     '',                           # Set to empty string for default. Not used with sqlite3.
    }
}

#==============================================================================
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'

#==============================================================================
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Whether a user's session cookie expires when the Web browser is closed.
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#==============================================================================
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_PATH, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_PATH, "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

#==============================================================================
# This should be deprecated in 1.4
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

#==============================================================================
# Frontend themes url (apps.frontend)
THEMES_URL = 'themes/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_PATH, "templates"),
    os.path.join(MEDIA_ROOT, THEMES_URL),
)

#==============================================================================
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
)

#==============================================================================
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

#==============================================================================
ROOT_URLCONF = '%s.urls' % PROJECT_DIRNAME

#==============================================================================
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    "django.contrib.redirects",
    'django.contrib.sessions',
    'django.contrib.sites',
    "django.contrib.sitemaps",
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'grappelli.dashboard',
    'grappelli',
    'filebrowser',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'tagging',
    'smuggler',
    'mptt',

    '%s.library' % PROJECT_DIRNAME, # core library
    '%s.data' % PROJECT_DIRNAME, # initial import of custom fixtures

    '%s.apps.base' % PROJECT_DIRNAME,
    '%s.apps.batchimport' % PROJECT_DIRNAME,
    '%s.apps.config' % PROJECT_DIRNAME,
    '%s.apps.contribute' % PROJECT_DIRNAME,
    '%s.apps.custom' % PROJECT_DIRNAME,
    '%s.apps.definitions' % PROJECT_DIRNAME,
    '%s.apps.frontend' % PROJECT_DIRNAME,
    '%s.apps.mail' % PROJECT_DIRNAME,
    '%s.apps.mobile' % PROJECT_DIRNAME,
    '%s.apps.search' % PROJECT_DIRNAME,
    '%s.apps.social' % PROJECT_DIRNAME,
)

#==============================================================================
# apps.social
AUTHENTICATION_BACKENDS = (
    '%s.apps.social.auth.OpenIDBackend' % PROJECT_DIRNAME,
) + AUTHENTICATION_BACKENDS

# Should users be created when new OpenIDs are used to log in?
OPENID_CREATE_USERS = True

# When logging in again, should we overwrite user details based on
# data received via Simple Registration?
OPENID_UPDATE_DETAILS_FROM_SREG = True

# Should django_auth_openid be used to sign into the admin interface?
OPENID_USE_AS_ADMIN_LOGIN = True

# Force login with google
OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/id'

# Tell django.contrib.auth to use the OpenID signin URLs.
LOGIN_URL = '/openid/login/'
LOGIN_REDIRECT_URL = '/'

#==============================================================================
# Django Rules
INSTALLED_APPS += ('django_rules',)
CENTRAL_AUTHORIZATIONS = '%s.auth' % PROJECT_DIRNAME
AUTHENTICATION_BACKENDS += (
    'django_rules.backends.ObjectPermissionBackend',
)

#==============================================================================
# Django Filebrowser
FILEBROWSER_MAX_UPLOAD_SIZE = get_config('MAX_UPLOAD_SIZE', 10485760)
FILEBROWSER_DIRECTORY = ''
FILEBROWSER_EXTENSIONS = {
    'Image': ['.jpg','.jpeg','.gif','.png','.tif','.tiff'],
    'Document': ['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Video': ['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Audio': ['.mp3','.mp4','.wav','.aiff','.midi','.m4p']
}

#==============================================================================
# BatchImport (apps.batchimport)
BATCH_IMPORT_IMPORTABLE_MODELS = ['base.Contact']
BATCH_IMPORT_UPDATE_DUPS = True
BATCH_IMPORT_UNEDITABLE_FIELDS = False

#==============================================================================
# CKeditor (library)
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            [      'Undo', 'Redo',
              '-', 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord',
              '-', 'Format', 'Font', 'FontSize',
              '-', 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript',
              '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',
            ],
            [
                   'Image', 'YoutubeEmbed', 'Table', 'HorizontalRule', 'SpecialChar', 'PageBreak', 'Iframe',
              '-', 'Link', 'Unlink', 'Anchor',
              '-', 'BulletedList', 'NumberedList',
              '-', 'Source',
              '-', 'Maximize', 'CustomPlaceHolder'
            ],
        ],
        'width': 763,
        'height': 320,
        'toolbarCanCollapse': False,
        'extraPlugins': 'CustomPlaceHolder,MediaEmbed',
    }
}

#==============================================================================
# Django Grappelli
GRAPPELLI_ADMIN_TITLE = SITE_NAME
GRAPPELLI_INDEX_DASHBOARD = '%s.dashboard.CustomIndexDashboard' % PROJECT_DIRNAME
ADMIN_MEDIA_PREFIX = STATIC_URL + 'grappelli/'

#==============================================================================
# Django Debug Toolbar
try:
    from debug_toolbar import VERSION as _DEBUG_TOOLBAR_VERSION
    _INSTALL_DEBUG_TOOLBAR = True
except:
    _INSTALL_DEBUG_TOOLBAR = False

if DEBUG and _INSTALL_DEBUG_TOOLBAR:
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        #'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
        #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
        'HIDE_DJANGO_SQL': False,
        'ENABLE_STACKTRACES' : False,
        'TAG': 'div',
    }
    DEBUG_TOOLBAR_PANELS = (
        #'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        #'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        #'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

#==============================================================================
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGLEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)-15s] [%(levelname)s ] %(pathname)s line %(lineno)d: %(message)s' # %(process)d %(thread)d
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': LOGLEVEL,
            'class': 'django.utils.log.NullHandler',
        },
        'console':{
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': LOGLEVEL,
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': LOGLEVEL,
            'propagate': True,
        },
    }
}
