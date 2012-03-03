# -*- coding: utf-8 -*-

import os

#==============================================================================
def force_reload():
    LIBRARY_PATH = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    ROOT_PATH = os.path.split(LIBRARY_PATH)[0]
    settings_file = os.path.join(ROOT_PATH, 'settings.py')

    print "WARNING: experimental reload !"

    os.system('touch %s' % os.path.abspath(settings_file))
    
    # TODO - in testing
    #def touch(fname, times = None):
    #    with file(fname, 'a'): os.utime(fname, times)
    #touch(os.path.abspath(settings_file))
