# -*- coding: utf-8 -*-

import re
from django import forms, template
from django.db import models, transaction, router
from django.contrib import admin
from django.contrib.admin import widgets, helpers
from django.conf.urls.defaults import url, patterns
from django.core import urlresolvers
from django.http import Http404, HttpResponseRedirect
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.shortcuts import get_object_or_404, render_to_response

from .views.change_list import BaseChangeList
from .actions import *


#==============================================================================
class RootAdmin(admin.ModelAdmin):
    """
    The root admin, should be left blank
    """
    pass


#==============================================================================
class DisplayViewAdmin(RootAdmin):
    """
    Add a view to display the models (no forms)
    """

    #--------------------------------------------------------------------------    
    def __init__(self, *args, **kwargs):
        super(DisplayViewAdmin, self).__init__(*args, **kwargs)

    #--------------------------------------------------------------------------    
    def display_view(self, request, object_id, extra_context=None):
        
        opts = self.model._meta
        app_label = opts.app_label        
        media = self.media
        
        try:
            obj = self.model._default_manager.get(pk=object_id)
        except:
            raise Http404

        ModelForm = self.get_form(request, obj)
        formsets = []

        form = ModelForm(instance=obj)
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request, obj), self.inline_instances):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(instance=obj, prefix=prefix,
                              queryset=inline.queryset(request))
            formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.prepopulated_fields, self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('View %s') % (obj),
            'opts': opts,
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'has_change_permission': self.has_change_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }

        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.change_list_template or [
            'admin/%s/%s/view_form.html' % (app_label, opts.object_name.lower()),
            'admin/%s/view_form.html' % app_label,
            'admin/view_form.html'
        ], context, context_instance=context_instance)

    #--------------------------------------------------------------------------    
    def redirect_view(self, request, object_id, extra_context=None):
        info = self.model._meta.app_label, self.model._meta.module_name
        return HttpResponseRedirect(urlresolvers.reverse('admin:%s_%s_changelist' % info))
        
    #--------------------------------------------------------------------------    
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^add/$',
                wrap(self.add_view),
                name='%s_%s_add' % info),
            url(r'^(.+)/history/$',
                wrap(self.history_view),
                name='%s_%s_history' % info),
            url(r'^(.+)/delete/$',
                wrap(self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(.+)/view/$',
                wrap(self.display_view),
                name='%s_%s_view' % info),
            url(r'^(.+)/change/$',
                wrap(self.change_view),
                name='%s_%s_change' % info),
            url(r'^(.+)/$',
                wrap(self.redirect_view),
                name='%s_%s_redirect' % info),
        )
        return urlpatterns


        urlpatterns = patterns('',
        )
        return urlpatterns + super(DisplayViewAdmin, self).get_urls()

    #--------------------------------------------------------------------------    
    def get_changelist(self, request, **kwargs):
        return BaseChangeList


#==============================================================================
class RedirectableAdmin(DisplayViewAdmin):
    """
    The redirectable admin, that correctly redirects after a filter has been choosen
    """

    #--------------------------------------------------------------------------    
    def add_view(self, request, *args, **kwargs):
        """
        Used to redirect users back to their filtered list of locations if there were any
        """
        result = super(RedirectableAdmin, self).add_view(request, *args, **kwargs)

       # Look at the referer for a query string '^.*\?.*$'
        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            # We've got a query string, set the session value
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            """
            We only kick into action if we've saved and if
            there is a session key of 'filtered', then we
            delete the key.
            """
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass
        return result

    #--------------------------------------------------------------------------    
    def change_view(self, request, object_id, extra_context={}):
        """
        Save the referer of the page to return to the filtered change_list after saving the page
        """
        result = super(RedirectableAdmin, self).change_view(request, object_id, extra_context)

        # Look at the referer for a query string '^.*\?.*$'
        ref = request.META.get('HTTP_REFERER', '')
        if ref.find('?') != -1:
            # We've got a query string, set the session value
            request.session['filtered'] =  ref

        if request.POST.has_key('_save'):
            """
            We only kick into action if we've saved and if
            there is a session key of 'filtered', then we
            delete the key.
            """
            try:
                if request.session['filtered'] is not None:
                    result['Location'] = request.session['filtered']
                    request.session['filtered'] = None
            except:
                pass
        return result


#==============================================================================
class ButtonableAdmin(DisplayViewAdmin): #(RedirectableAdmin):
    """
    A subclass of this admin will let you add buttons (like history) in the
    change view of an entry.

    ex.
    class FooAdmin(ButtonAdmin):
       ...

       def bar(self, request, obj=None):
          if obj != None: obj.bar()
          return None # Redirect or Response or None
       bar.short_description='Example button'

       list_buttons = [ bar ]
       change_buttons = [ bar ]
       view_buttons = [ bar ]

    you can then put the following in your admin/change_form.html template:

       {% block object-tools %}
           {% if change %}{% if not is_popup %}
           <ul class="object-tools">
           {% for button in buttons %}
             <li><a href="{{ button.func_name }}/">{{ button.short_description }}</a></li>
           {% endfor %}
           <li><a href="history/" class="historylink">History</a></li>
           {% if has_absolute_url %}<li><a href="../../../r/{{ content_type_id }}/{{ object_id }}/" class="viewsitelink">View on site</a></li>{% endif%}
           </ul>
           {% endif %}{% endif %}
       {% endblock %}

    """

    change_buttons=[]
    list_buttons=[]
    view_buttons=[]

    #--------------------------------------------------------------------------    
    def button_view_dispatcher(self, request, url):
        # Dispatch the url to a function call
        if url is not None:
            res = re.match('(.*/)?(?P<id>\d+)/(?P<view>.*)/(?P<command>.*)$', url)
            if res:
                button_list = {'view': self.view_buttons, 'change': self.change_buttons }
                if res.group('command') in [b.func_name for b in button_list[res.group('view')]]:
                    obj = self.model._default_manager.get(pk=res.group('id'))
                    response = getattr(self, res.group('command'))(request, obj)
                    if response is None:
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
                    return response

            res = re.match('(.*/)?(?P<id>\d+)/(?P<command>.*)$', url)
            if res:
                if res.group('command') in [b.func_name for b in self.change_buttons]:
                    obj = self.model._default_manager.get(pk=res.group('id'))
                    response = getattr(self, res.group('command'))(request, obj)
                    if response is None:
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
                    return response

            res = re.match('(.*/)?(?P<command>.*)$', url)
            if res:
                if res.group('command') in [b.func_name for b in self.list_buttons]:
                    response = getattr(self, res.group('command'))(request)
                    if response is None:
                        return HttpResponseRedirect(request.META['HTTP_REFERER'])
                    return response

        # Delegate to the appropriate method, based on the URL.
        from django.contrib.admin.util import unquote
        if url is None:
            return self.changelist_view(request)
        elif url == 'add':
            return self.add_view(request)
        elif url.endswith('/history'):
            return self.history_view(request, unquote(url[:-8]))
        elif url.endswith('/delete'):
            return self.delete_view(request, unquote(url[:-7]))
        elif url.endswith('/change'):
            return self.change_view(request, unquote(url[:-7]))
        elif url.endswith('/view'):
            return self.display_view(request, unquote(url[:-5]))
        else:
            return self.display_view(request, unquote(url))

    #--------------------------------------------------------------------------    
    def get_urls(self):
        from django.conf.urls.defaults import url, patterns
        from django.utils.functional import update_wrapper
        # Define a wrapper view
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        #  Add the custom button url
        urlpatterns = patterns('',
            url(r'^(.+)/$', wrap(self.button_view_dispatcher),)
        )
        return urlpatterns + super(ButtonableAdmin, self).get_urls()

    #--------------------------------------------------------------------------    
    def display_view(self, request, object_id, extra_context=None):
        if not extra_context: extra_context = {}
        if hasattr(self, 'view_buttons'):
            extra_context['buttons'] = self._convert_buttons(self.view_buttons)
        if '/' in object_id:
            object_id = object_id[:object_id.find('/')]
        return super(ButtonableAdmin, self).display_view(request, object_id, extra_context)

    #--------------------------------------------------------------------------    
    def change_view(self, request, object_id, extra_context=None):
        if not extra_context: extra_context = {}
        if hasattr(self, 'change_buttons'):
            extra_context['buttons'] = self._convert_buttons(self.change_buttons)
        if '/' in object_id:
            object_id = object_id[:object_id.find('/')]
        return super(ButtonableAdmin, self).change_view(request, object_id, extra_context)

    #--------------------------------------------------------------------------    
    def changelist_view(self, request, extra_context=None):
        if not extra_context: extra_context = {}
        if hasattr(self, 'list_buttons'):
            extra_context['buttons'] = self._convert_buttons(self.list_buttons)
        return super(ButtonableAdmin, self).changelist_view(request, extra_context)

    #--------------------------------------------------------------------------    
    def _convert_buttons(self, orig_buttons):
        buttons = []
        for b in orig_buttons:
            buttons.append({ 'func_name': b.func_name, 'short_description': b.short_description })
        return buttons


#===============================================================================
class BaseAdmin(ButtonableAdmin):
    """
    The base admin for every admin in this application
    """
    
    #save_as = True
    date_hierarchy = 'created'
    
    #--------------------------------------------------------------------------    
    def __init__(self, *args, **kwargs):
        super(BaseAdmin, self).__init__(*args, **kwargs)

    #--------------------------------------------------------------------------    
    def get_actions(self, request):
        actions = super(BaseAdmin, self).get_actions(request)
        #if 'delete_selected' in actions:
        #    del actions['delete_selected']
        return actions
