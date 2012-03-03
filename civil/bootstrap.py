# -*- coding: utf-8 -*-

import os, sys

BASE_PATH = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
THIRDPARTY_PATH = os.path.normpath(os.path.join(BASE_PATH, 'thirdparty'))

PROJECT_DIRNAME = os.path.dirname(os.path.abspath(__file__)).split(os.sep)[-1]

def insert_if_not_exists(path, silent=False):
    if not os.path.exists(path):
        if not silent:
            raise IOError("Cannot bootstrap with missing '%s' directory !" % path)
    if not sys.path.__contains__(path):
        sys.path.insert(0, path)

# application path
insert_if_not_exists(BASE_PATH)

# libraries
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "html5lib-0.90/src")) # beautifulsoup
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "BeautifulSoup-3.2.0")) # html parsing
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "xlrd-0.6.1")) # batchimport

# django paths
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "Django-1.3.1"))

# direct dependencies
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-mptt")) # hierarchical trees
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-smuggler")) # fixture i/o
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-tagging")) # tagging
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-filebrowser")) # filebrowser
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-grappelli")) # grappelli
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-rules")) # permissions

# testing
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "python-openid-2.2.5")) # django-social-auth
#insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "httplib2-0.7.2/python2")) # oauth2
#insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "oauth2-1.5.167")) # django-social-auth

#insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-social-auth"))
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-openid-auth"))

# debug only
insert_if_not_exists(os.path.join(THIRDPARTY_PATH, "django-debug-toolbar"), silent=True) # debug toolbar

# be sure we load the correct settings
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % PROJECT_DIRNAME
