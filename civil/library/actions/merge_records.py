# -*- coding: utf-8 -*-

import datetime
from collections import defaultdict
from django import forms
from django.db import models, transaction
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
def get_model_from_name(model_name):
    for m in models.get_models():
        if m._meta.verbose_name == model_name:
            return m
    return None


#==============================================================================
def get_field_from_model(model, name):
    return model._meta.get_field_by_name(name)[0]


#==============================================================================
def get_through_foreign_key_field(through_model, model):
    for f in through_model._meta.fields:
        # TODO - handle multiple foreignkey in through models
        if isinstance(f, models.ForeignKey) and f.rel.to == model:
            return f
    return None


#==============================================================================
def model_is_through_of(model_to_check, model):
    for f in model._meta.local_many_to_many:
        if model_to_check == f.rel.through:
            return True
    return False


#==============================================================================
def get_models_related_to(model):
    additionals = {}
    for m in models.get_models():
        if m._meta.proxy:
            continue
        for f in m._meta.fields:
            #if model_is_through_of(m, model):
            #    continue
            if isinstance(f, models.ForeignKey) and f.rel.to == model:
                model_name = m._meta.verbose_name
                model_name_plural = m._meta.verbose_name_plural
                if model_name not in additionals:
                    additionals[model_name] = { 'model': m,
                                                'verbose_name': model_name,
                                                'verbose_name_plural': model_name_plural,
                                                'fields': m._meta.fields }
    return [additionals[key] for key in sorted(additionals, key=additionals.get)]



#==============================================================================
class MergeRecordForm(forms.ModelForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    _keep_left = forms.BooleanField(label=_('Keep left object'),
                                    initial=True, required=False,
                                    help_text=_('Keep the record on the left after merging (Delete the right one)'))

    def __init__(self, *args, **kwargs):
        super(MergeRecordForm, self).__init__(*args, **kwargs)

    def _clean_fields(self):
        # get main objects id        
        self.cleaned_data['pk_left'] = int(self.data.get('pk_left', 0))
        self.cleaned_data['pk_right'] = int(self.data.get('pk_right', 0))
        self.cleaned_data['_keep_left'] = self.data.get('_keep_left', '') == 'on'
        
        # get changing fields
        for name, field in self.fields.items():
            enabler = 'copy_id_%s' % name
            value = self.data.get(enabler, False)
            if value:
                self.cleaned_data[enabler] = value == 'left'

        # get additional models referring to this
        additional_models = get_models_related_to(self._meta.model)
        for model in additional_models:
            enabler = u'model_id_%s' % model['verbose_name']
            value = self.data.get(enabler, False)
            if value:
                self.cleaned_data[enabler] = value == 'left'

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
        m2m_fields = [field.name for field in self._meta.model._meta.local_many_to_many]
        return [field for field in self if not field.name.startswith('_') and field.name not in m2m_fields]


#==============================================================================
def merge_records_action(description=_("Merge records")):

    #@transaction.commit_on_success
    def merge_records(modeladmin, request, queryset):
        """
            Merge two records togheter action
        """

        additional_models = get_models_related_to(modeladmin.model)

        form = None
        FormClass = modelform_factory(modeladmin.model, form=MergeRecordForm)
        if 'apply' in request.POST:
            form = FormClass(request.POST)
            if form.is_valid():
                keep_left = form.cleaned_data.get('_keep_left', False)
                pk_left = form.cleaned_data.get('pk_left', 0)
                pk_right = form.cleaned_data.get('pk_right', 0)
                
                left = modeladmin.model.objects.get(pk=pk_left)
                right = modeladmin.model.objects.get(pk=pk_right)
                
                for key in form.cleaned_data.keys():
                    if key.startswith('copy_id_'):
                        field_name = key[8:]
                        field = get_field_from_model(modeladmin.model, field_name)
                        if isinstance(field, models.ManyToManyField):
                            continue # do not copy many to many
                        else:
                            key_to_left = form.cleaned_data.get(key, False)
                            if keep_left:
                                if not key_to_left: # right to left
                                    setattr(left, field_name, getattr(right, field_name))
                            else:
                                if key_to_left: # left to right
                                    setattr(right, field_name, getattr(left, field_name))
                    elif key.startswith('model_id_'):
                        model_name = key[9:]
                        key_to_left = form.cleaned_data.get(key, False)
                        model = get_model_from_name(model_name)
                        if not model:
                            print "Cannot find model" # TODO - remove
                            continue
                        field = get_through_foreign_key_field(model, modeladmin.model)
                        if not field:
                            print "Cannot find field" # TODO - remove
                            continue
                        if keep_left:
                            if not key_to_left: # right to left
                                results = model.objects.filter(**{ '%s' % field.name: pk_right })
                                for r in results:
                                    setattr(r, field.name, modeladmin.model.objects.get(pk=pk_left))
                                    r.save()
                        else:
                            if key_to_left: # left to right
                                results = model.objects.filter(**{ '%s' % field.name: pk_left })
                                for r in results:
                                    setattr(r, field.name, modeladmin.model.objects.get(pk=pk_right))
                                    r.save()

                if keep_left:
                    merge_order = (right.__unicode__(), left.__unicode__())
                    left.save()
                    right.delete()
                else:
                    merge_order = (left.__unicode__(), right.__unicode__())
                    right.save()
                    left.delete()
                
                modeladmin.message_user(request, "Successfully merged record %s with %s." % merge_order)
                return HttpResponseRedirect(request.get_full_path())
            else:
                messages.error(request, _("Please correct the errors below"))

        if not form:
            initial = { admin.helpers.ACTION_CHECKBOX_NAME: request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME) }
            form = FormClass(initial=initial)
    
        adminForm = admin.helpers.AdminForm(form, modeladmin.get_fieldsets(request), {}, [], model_admin=modeladmin)
        media = modeladmin.media + adminForm.media
        
        records = queryset.all()
        if records.count() != 2:
            messages.error(request, _("Can merge only 2 records at the same time"))
            return HttpResponseRedirect(request.get_full_path())
        
        return render_to_response('admin/actions/merge_records.html',
            RequestContext(request, {'adminform': adminForm,
                                     'form': form,
                                     'title': _("Merge %s") % modeladmin.opts.verbose_name_plural,
                                     'left': records[0],
                                     'right': records[1],
                                     'additional_models': additional_models,
                                     'change': True,
                                     'is_popup': False,
                                     'save_as': False,
                                     'has_delete_permission': False,
                                     'has_add_permission': False,
                                     'has_change_permission': True,
                                     'opts': modeladmin.model._meta,
                                     'app_label': modeladmin.model._meta.app_label,
                                     'action': 'merge_records',
                                     'media': mark_safe(media),
                                     'selection': queryset,
                                     }))

    merge_records.short_description = description
    return merge_records
