# -*- coding: utf-8 -*-

from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.itercompat import is_iterable

from grappelli.dashboard.modules import DashboardModule

from civil.apps.search.models import SavedSearch, SavedSearchItem


#==============================================================================
class SavedSearches(DashboardModule):
    """
    A module that displays a list of saved searches.
    """
    
    title = _('Saved Search')
    template = 'grappelli/dashboard/modules/link_list.html'
    class_name = 'link-list'
    limit = 10
    
    def init_with_context(self, context):
        if self._initialized:
            return
        request = context['request']
        new_children = []
        
        if self.limit <= 0:
            self.limit = limit
        
        searches = SavedSearch.objects.filter(user=request.user).order_by('-when')[:self.limit]
        for s in searches:
            link_dict = { 'title': s.name, 'url': s.path, 'external': False }
            items = SavedSearchItem.objects.filter(search=s).count()
            if items == 0: link_dict['description'] = "No selected objects"
            elif items == 1: link_dict['description'] = "1 selected object"
            elif items > 1: link_dict['description'] = "%d selected objects" % items
            new_children.append(link_dict)
        else:
            link_dict = { 'title': 'No searches defined', 'url': '.', 'external': True }
            new_children.append(link_dict)

        self.children = new_children
        self._initialized = True