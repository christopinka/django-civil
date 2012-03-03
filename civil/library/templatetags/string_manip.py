# -*- coding: utf-8 -*-

from django import template

register = template.Library()

#==============================================================================
@register.filter(name="endswith")
@template.defaultfilters.stringfilter
def endswith(value,arg):
    return value.endswith(arg)
    