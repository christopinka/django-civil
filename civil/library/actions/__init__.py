# -*- coding: utf-8 -*-

from .delete_all import delete_all_action
from .export_to_csv import export_to_csv_action
from .export_as_csv import export_as_csv_action
from .graph_queryset import graph_queryset_action
from .mass_update import mass_update_action
from .merge_records import merge_records_action
from .save_search import save_search_action

#from .test_queryset import test_queryset_action

#===============================================================================
from django.contrib import admin
admin.site.add_action(delete_all_action(), 'delete_all')
admin.site.add_action(export_to_csv_action(), 'export_to_csv')
admin.site.add_action(export_as_csv_action(), 'export_as_csv')
admin.site.add_action(graph_queryset_action(), 'graph_queryset')
admin.site.add_action(mass_update_action(), 'mass_update')
admin.site.add_action(merge_records_action(), 'merge_records')
admin.site.add_action(save_search_action(), 'save_search')
