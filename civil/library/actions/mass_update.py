# -*- coding: utf-8 -*-

import datetime
from collections import defaultdict
from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms.models import modelform_factory
from django.db.models.fields import BooleanField
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson as json
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


#==============================================================================
class MassUpdateForm(forms.ModelForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    _validate = forms.BooleanField(label=_('Validate'), help_text=_('if checked allows validating of many to many realtions'))

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, forms.models.ModelMultipleChoiceField) and value:
                    raise ValidationError(_("Unable to mass update many to many relation without using 'validate'"))

                if isinstance(field, forms.FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    enabler = 'chk_id_%s' % name
                    if self.data.get(enabler, False):
                        value = field.clean(value)
                        self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError, e:
                self._errors[name] = self.error_class(e.messages)
                if name in self.cleaned_data:
                    del self.cleaned_data[name]

    def clean__validate(self):
        return self.data.get('_validate', '') == 'on'

    def _post_clean(self):
        # avoid running internals of _post_clean
        pass

    def configured_fields(self):
        """
        Returns a list of BoundField objects that aren't hidden fields, and
        is the opposite of the hidden_fields() method.
        This is onlt used in the template.
        """
        return [field for field in self if not field.is_hidden and field.name.startswith('_')]

    def model_fields(self):
        """
        Returns a list of BoundField objects that aren't "private" fields.
        This is only used in the template.
        """
        return [field for field in self if not field.name.startswith('_')]


#==============================================================================
def mass_update_action(description=_("Mass update")):

    def mass_update(modeladmin, request, queryset):
        """
            mass update queryset
        """
        form = None
        FormClass = modelform_factory(modeladmin.model, form=MassUpdateForm)
        if 'apply' in request.POST:
            form = FormClass(request.POST)
            if form.is_valid():
                done = 0
                if form.cleaned_data.get('_validate', False):
                    for record in queryset:
                        for k, v in form.cleaned_data.items():
                            setattr(record, k, v)
                            record.save()
                            done += 1
                    messages.info(request, "Updated %s records" % done)
                else:
                    values = {}
                    for field_name, value in form.cleaned_data.items():
                        if isinstance(form.fields[field_name], forms.models.ModelMultipleChoiceField):
                            messages.error(request, _("Unable to mass update many to many relation without using 'validate'"))
                            return HttpResponseRedirect(request.get_full_path())
                        elif field_name not in ['_selected_action', '_validate']:
                            values[field_name] = value
                    queryset.update(**values)
                return HttpResponseRedirect(request.get_full_path())
            else:
                messages.error(request, _("Please correct the errors below"))

        grouped = defaultdict(lambda: [])

        if not form:
            initial = { admin.helpers.ACTION_CHECKBOX_NAME: request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)}
            for el in queryset.all()[:10]:
                for f in modeladmin.model._meta.fields:
                    if hasattr(f, 'flatchoices') and f.flatchoices:
                        grouped[f.name] = dict(getattr(f, 'flatchoices')).values()
                    elif hasattr(f, 'choices') and f.choices:
                        grouped[f.name] = dict(getattr(f, 'choices')).values()
                    elif isinstance(f, BooleanField):
                        grouped[f.name] = [True, False]
                    else:
                        value = getattr(el, f.name)
                        if value is not None and value not in grouped[f.name]:
                            grouped[f.name].append(value)
                    initial[f.name] = initial.get(f.name, value)
            form = FormClass(initial=initial)
    
        adminForm = admin.helpers.AdminForm(form, modeladmin.get_fieldsets(request), {}, [], model_admin=modeladmin)
        media = modeladmin.media + adminForm.media
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.date) else str(obj)
    
        return render_to_response('admin/actions/mass_update.html',
            RequestContext(request, {'adminform': adminForm,
                                     'form': form,
                                     'title': _("Mass update %s") % modeladmin.opts.verbose_name_plural,
                                     'grouped': grouped,
                                     'fieldvalues': json.dumps(grouped, default=dthandler),
                                     'change': True,
                                     'is_popup': False,
                                     'save_as': False,
                                     'has_delete_permission': False,
                                     'has_add_permission': False,
                                     'has_change_permission': True,
                                     'opts': modeladmin.model._meta,
                                     'app_label': modeladmin.model._meta.app_label,
                                     'action': 'mass_update',
                                     'media': mark_safe(media),
                                     'selection': queryset,
                                     }))

    mass_update.short_description = description
    return mass_update
