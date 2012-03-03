# -*- coding: utf-8 -*-

from os.path import dirname, abspath, split, join

#==============================================================================
_APPS_PATH = split(abspath(dirname(__file__)))[0]

#==============================================================================
_ROOT_PATH = split(_APPS_PATH)[0]
_DATABASE_PATH = join(_ROOT_PATH, "database")

#==============================================================================
CONFIG_FILE = join(_DATABASE_PATH, "default.json")
