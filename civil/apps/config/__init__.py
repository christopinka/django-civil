# -*- coding: utf-8 -*-

from .settings import CONFIG_FILE
from django.utils import simplejson


#==============================================================================
def _get_config_data():
    config_file = open(CONFIG_FILE, "r")
    data = simplejson.loads(config_file.read())
    config_file.close()
    return data


#==============================================================================
def get_config(name, default=None):
    data = _get_config_data()
    try:
        return data[name]
    except:
        return default


#==============================================================================
def get_config_integer(name, default=0):
    data = _get_config_data()
    try:
        return int(data[name])
    except:
        return default


#==============================================================================
def get_config_float(name, default=0.0):
    data = _get_config_data()
    try:
        return float(data[name])
    except:
        return default


#==============================================================================
def get_config_boolean(name, default=False):
    data = _get_config_data()
    try:
        return bool(data[name])
    except:
        return default
