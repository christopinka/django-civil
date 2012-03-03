# -*- coding: utf-8 -*-

import csv, datetime
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.contrib.admin import helpers
from django.utils import formats
from django.utils import dateformat


#==============================================================================
DELIMITERS = ",;|:"
QUOTES = "'\"`"
ESCAPECHARS = " \\"


#==============================================================================
class CSVOptions(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    header = forms.BooleanField(initial=True, required=False)
    delimiter = forms.ChoiceField(choices=zip(DELIMITERS, DELIMITERS))
    quotechar = forms.ChoiceField(choices=zip(QUOTES, QUOTES))
    quoting = forms.ChoiceField(choices=((csv.QUOTE_ALL, 'All'),
                                         (csv.QUOTE_MINIMAL, 'Minimal'),
                                         (csv.QUOTE_NONE, 'None'),
                                         (csv.QUOTE_NONNUMERIC, 'Non Numeric')))
    escapechar = forms.ChoiceField(choices=(('', ''), ('\\', '\\')), required=False)
    datetime_format = forms.CharField(initial=formats.get_format('SHORT_DATETIME_FORMAT'))
    date_format = forms.CharField(initial=formats.get_format('SHORT_DATE_FORMAT'))
    time_format = forms.CharField(initial=formats.get_format('TIME_FORMAT'))
    null_as = forms.CharField(initial='', required=False)
    columns = forms.MultipleChoiceField()


#==============================================================================
def export_to_csv_action(description=_("Export to CSV file (Expert)")):

    def export_to_csv(modeladmin, request, queryset):
        """
            export a queryset to csv file
        """
        cols = [(f.name, f.verbose_name) for f in queryset.model._meta.fields]
        initial = { helpers.ACTION_CHECKBOX_NAME: request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
                    'columns': [x for x, v in cols],
                    'quotechar': '"',
                    'quoting': csv.QUOTE_ALL,
                    'delimiter': '|',
                    'escapechar': '\\', }
    
        if 'apply' in request.POST:
            form = CSVOptions(request.POST)
            form.fields['columns'].choices = cols
            if form.is_valid():
                response = HttpResponse(mimetype='text/csv')
                response['Content-Disposition'] = \
                    'attachment;filename="%s.csv"' % queryset.model._meta.verbose_name_plural.lower().replace(" ", "_")
                try:
                    writer = csv.writer(response,
                                        escapechar=str(form.cleaned_data['escapechar']),
                                        delimiter=str(form.cleaned_data['delimiter']),
                                        quotechar=str(form.cleaned_data['quotechar']),
                                        quoting=int(form.cleaned_data['quoting']))

                    if form.cleaned_data.get('header', False):
                        writer.writerow([f for f in form.cleaned_data['columns']])
    
                    for obj in queryset:
                        row = []
                        for fieldname in form.cleaned_data['columns']:
                            if hasattr(obj, 'get_%s_display' % fieldname):
                                value = getattr(obj, 'get_%s_display' % fieldname)()
                            else:
                                value = getattr(obj, fieldname)
                            if isinstance(value, datetime.datetime):
                                value = dateformat.format(value, form.cleaned_data['datetime_format'])
                            elif isinstance(value, datetime.date):
                                value = dateformat.format(value, form.cleaned_data['date_format'])
                            elif isinstance(value, datetime.time):
                                value = dateformat.format(value, form.cleaned_data['time_format'])
                            if value is None: value = form.cleaned_data['null_as']
                            row.append(smart_str(value))
                        writer.writerow(row)
                except Exception, e:
                    messages.error(request, "Error: (%s)" % str(e))
                else:
                    return response
        else:
            form = CSVOptions(initial=initial)
            form.fields['columns'].choices = cols
    
        adminForm = helpers.AdminForm(form, modeladmin.get_fieldsets(request), {}, [], model_admin=modeladmin)
        media = modeladmin.media + adminForm.media
        return render_to_response('admin/actions/export_to_csv.html',
                                  RequestContext(request, {'adminform': adminForm,
                                                           'form': form,
                                                           'change': True,
                                                           'title': description,
                                                           'is_popup': False,
                                                           'save_as': False,
                                                           'has_delete_permission': False,
                                                           'has_add_permission': False,
                                                           'has_change_permission': True,
                                                           'opts': queryset.model._meta,
                                                           'app_label': queryset.model._meta.app_label,
                                                           'action': 'export_to_csv',
                                                           'media': mark_safe(media),
                                                           }))
    export_to_csv.short_description = description
    return export_to_csv