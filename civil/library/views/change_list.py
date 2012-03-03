# -*- coding: utf-8 -*-

import operator
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.util import quote


#==============================================================================
class BaseChangeList(ChangeList):

    def url_for_result(self, result):
        return "%s/view/" % quote(getattr(result, self.pk_attname))
