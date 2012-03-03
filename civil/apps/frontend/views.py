# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Context, Template
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _

from .models import *


#==============================================================================
def _render_page_content(content, request):
    t = Template(content)    
    return t.render(RequestContext(request))

def _build_page_object(page, request):
    return {
        'page': {
            'name': page.name,
            'slug': page.slug,
            'status': page.status,
            'access': page.access,
            'author': page.author,
            'parent': page.parent,
            'children': page.children,
            'title': page.title,
            'keywords': page.keywords,
            'description': page.description,
            'excerpt': _render_page_content(page.excerpt, request),
            'content': _render_page_content(page.content, request),
            'publish_date': page.publish_date,
            'expiration_date': page.expiration_date,
            'is_index': page.is_index,
        }
    }

def _render_page(theme, page, request):
    # TODO - check status
    # TODO - check access level
    
    template = [
        '{%% extends "%s/main.html" %%}' % (theme.slug),
        '{% load url from future %}',
    ]
    
    for position in ThemePlaceholder.objects.filter(theme=theme):
        template.append('{%% block %s %%}' % (position.name))
        for plug in PluginPosition.objects.filter(position=position, status=STATUS_PUBLISHED).order_by('order'):
            # TODO - check status
            if request.user.is_authenticated():
                if plug.access == ACCESS_PUBLIC_ONLY:
                    continue
            else:
                if plug.access == ACCESS_RESTRICTED:
                    continue
            plugin = plug.plugin.load()
            inst = plugin.PluginClass()
            # TODO - handle plugin render
            template.append(inst.render(page, plug))
        template.append('{% endblock %}')
    
    # print "\n".join(template)
    
    t = Template("\n".join(template))
    c = RequestContext(request, _build_page_object(page, request))
    return HttpResponse(t.render(c))    


#==============================================================================
def display_index(request):
    theme = Theme.get_default()
    page = get_object_or_404(Page, is_index=True, status=STATUS_PUBLISHED)
    return _render_page(theme, page, request)


#==============================================================================
def display_page_by_slug(request, slug):
    theme = Theme.get_default()
    page = get_object_or_404(Page, slug=slug, status=STATUS_PUBLISHED)
    return _render_page(theme, page, request)


#==============================================================================
def display_page_by_id(request, id):
    theme = Theme.get_default()
    page = get_object_or_404(Page, pk=id, status=STATUS_PUBLISHED)
    return _render_page(theme, page, request)


#==============================================================================
def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # TODO - Redirect to a success page.
            messages.info(request, _('Login successful.'))
            return HttpResponseRedirect('/')
        else:
            # TODO - Return a 'disabled account' error message.
            messages.error(request, _('Your account has been disabled.'))
            return HttpResponseRedirect('/')
    else:
        # TODO - Return an 'invalid login' error message.
        messages.error(request, _('Invalid username or password specified.'))
        return HttpResponseRedirect('/')


#==============================================================================
def logout_view(request):
    logout(request)
    messages.info(request, _('Logout successful.'))
    return HttpResponseRedirect('/')
