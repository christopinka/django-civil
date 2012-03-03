# -*- coding: utf-8 -*-

from django.template import add_to_builtins

#def add_tags_to_builtins(clazz):
#    import sys
#    try:
#        add_to_builtins("civil.library.customtags.%s" % clazz)
#    except:
#        import traceback
#        traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
#        sys.exit()
#
#add_tags_to_builtins('charts')
#add_tags_to_builtins('massupdate')

add_to_builtins('civil.library.templatetags.smart_extends')
