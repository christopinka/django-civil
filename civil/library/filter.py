# -*- coding: utf-8 -*-

from django.contrib.admin.filterspecs import FilterSpec
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _


#==============================================================================
# FilterSpec.register places the new FilterSpec at the back
# of the list. This can be a problem, because the first 
# matching FilterSpec is the one used.
def _register_front(cls, test, factory):
    cls.filter_specs.insert(0, (test, factory))

FilterSpec.register_front = classmethod(_register_front)


#==============================================================================
class NullFilterSpec(FilterSpec):
    fields = (models.CharField, models.TextField, models.IntegerField, models.PositiveIntegerField, models.FileField)
    
    def test(cls, field):
        return field.null and isinstance(field, cls.fields) and not field._choices
    test = classmethod(test)
    
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(NullFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_kwarg = '%s__isnull' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
    
    def choices(self, cl):
        # bool(v) must be False for IS NOT NULL and True for IS NULL, but can only be a string
        for k, v in ((_('All'), None), (_('Has value'), ''), (_('Omitted'), '1')):
            yield {
                'selected' : self.lookup_val == v,
                'query_string' : cl.get_query_string({self.lookup_kwarg : v}),
                'display' : k
            }
    
#FilterSpec.register_front(NullFilterSpec.test, NullFilterSpec)


#==============================================================================
class RelatedFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(RelatedFilterSpec, self).__init__(f, request, params, model, model_admin)
        if isinstance(f, models.ManyToManyField):
            self.lookup_title = f.rel.to._meta.verbose_name
        else:
            self.lookup_title = f.verbose_name
        rel_name = f.rel.get_related_field().name
        self.lookup_kwarg = '%s__%s__exact' % (f.name, rel_name)
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = f.get_choices(include_blank=False)

    def title(self):
        return self.lookup_title

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
               'display': _('All')}
        for pk_val, val in self.lookup_choices:
            yield {'selected': self.lookup_val == smart_unicode(pk_val),
                   'query_string': cl.get_query_string({self.lookup_kwarg: pk_val}, [self.lookup_kwarg]),
                   'display': val}

FilterSpec.register_front(lambda f: bool(f.rel) and (not hasattr(f, 'null') or not f.null), RelatedFilterSpec)


#==============================================================================
class RelatedNullFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(RelatedNullFilterSpec, self).__init__(f, request, params, model, model_admin)
        if isinstance(f, models.ManyToManyField):
            self.lookup_title = f.rel.to._meta.verbose_name
        else:
            self.lookup_title = f.verbose_name
        self.null_lookup_kwarg = '%s__isnull' % f.name
        self.null_lookup_val = request.GET.get(self.null_lookup_kwarg, None)
        rel_name = f.rel.get_related_field().name
        self.lookup_kwarg = '%s__%s__exact' % (f.name, rel_name)
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = f.get_choices(include_blank=False)

    def title(self):
        return self.lookup_title

    def choices(self, cl):
        yield {'selected': self.lookup_val is None and self.null_lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.null_lookup_kwarg]),
               'display': _('All')}
        yield {'selected': self.lookup_val is None and self.null_lookup_val == "True",
               'query_string': cl.get_query_string({self.null_lookup_kwarg: True}, [self.lookup_kwarg]),
               'display': _('(None)')}
        yield {'selected': self.lookup_val is None and self.null_lookup_val == "False",
               'query_string': cl.get_query_string({self.null_lookup_kwarg: False}, [self.lookup_kwarg]),
               'display': _('(Not None)')}
        for pk_val, val in self.lookup_choices:
            yield {'selected': self.lookup_val == smart_unicode(pk_val),
                   'query_string': cl.get_query_string({self.lookup_kwarg: pk_val}, [self.null_lookup_kwarg]),
                   'display': val}

FilterSpec.register_front(lambda f: bool(f.rel) and hasattr(f, 'null') and f.null, RelatedNullFilterSpec)


#==============================================================================
class NullNotNullChoicesFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(NullNotNullChoicesFilterSpec, self).__init__(f, request, params, model,
                                                           model_admin,
                                                           field_path=field_path)
        self.null_lookup_kwarg = '%s__isnull' % self.field_path
        self.null_lookup_val = request.GET.get(self.null_lookup_kwarg, None)
        self.lookup_kwarg = '%s__exact' % self.field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)

    def choices(self, cl):
        yield {'selected': self.lookup_val is None and self.null_lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.null_lookup_kwarg]),
               'display': _('All')}
        yield {'selected': self.lookup_val is None and self.null_lookup_val == "True",
               'query_string': cl.get_query_string({self.null_lookup_kwarg: True}, [self.lookup_kwarg]),
               'display': _('(None)')}
        yield {'selected': self.lookup_val is None and self.null_lookup_val == "False",
               'query_string': cl.get_query_string({self.null_lookup_kwarg: False}, [self.lookup_kwarg]),
               'display': _('(Not None)')}
        for k, v in self.field.flatchoices:
            yield {'selected': smart_unicode(k) == self.lookup_val,
                    'query_string': cl.get_query_string(
                                    {self.lookup_kwarg: k}),
                    'display': v}

FilterSpec.register_front(lambda f: bool(f.choices) and hasattr(f, 'null') and f.null, NullNotNullChoicesFilterSpec)
