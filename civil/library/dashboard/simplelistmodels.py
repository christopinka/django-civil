# -*- coding: utf-8 -*-

from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.itercompat import is_iterable

from grappelli.dashboard.modules import DashboardModule
from grappelli.dashboard.utils import AppListElementMixin


#==============================================================================
class SimpleModelList(DashboardModule, AppListElementMixin):
    """
    Module that lists a set of models.
    """
    
    template = 'grappelli/dashboard/modules/simple_model_list.html'
    class_name = 'link-list'
    models = None
    exclude = None
    
    def __init__(self, title=None, models=None, exclude=None, **kwargs):
        self.models = list(models or [])
        self.exclude = list(exclude or [])
        super(SimpleModelList, self).__init__(title, **kwargs)
    
    def init_with_context(self, context):
        if self._initialized:
            return
        items = self._visible_models(context['request'])
        if not items:
            return
        for model, perms in items:
            model_dict = {}
            model_dict['title'] = capfirst(model._meta.verbose_name_plural)
            if perms['change']:
                model_dict['url'] = self._get_admin_change_url(model, context)
            self.children.append(model_dict)
        self._initialized = True