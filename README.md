```                                                          
     _/_/_/  _/_/_/  _/      _/  _/_/_/  _/  
  _/          _/    _/      _/    _/    _/   
 _/          _/    _/      _/    _/    _/    
_/          _/      _/  _/      _/    _/     
 _/_/_/  _/_/_/      _/      _/_/_/  _/_/_/_/
```

## Introduction

### What is Django-CIVIL ?

It is a complete constituent relationship management and content management
system solution, especially built for non-profit and non-governmental groups.
The aim of the project is to build a fast, compact and maintainable aternative
to CiviCRM-Joomla, in a more pythonic and django-like flavour.

### Who will benefit of Django-CIVIL ?

Every cultural associations, with contributors and associations fees.
Amateur sports clubs can also benefit from this as it will allow to keep track
of incomes and user registrations for every year of service.
Anyone who needs to keep an eye on contacts and should send newsletters to them.


## Features

* contacts and groups management
* contribution system with payment registrations
* custom fields for most used objects
* newsletter system and mail tracking with logs
* frontend site with skins and plugins (TODO)
* frontend integration of contacts registration and payment (TODO)
* openid login enabled in frontend
* tagging system
* saved searches
* well organized admin dashboard
* batch import/export models from/to csv


## Strong points

* built with django
* administration built on top of django-admin and grappelli for the ease of use
* every model have a specialized changelist
* lot of custom model actions (export, merge, duplicate, graph)
* contacts can have on or more frontend users (django.apps.auth.user)
* online payment registration (future)


## Dependencies

* Django-1.3.1
* django-grappelli-2.3.5
* django-filebrowser-3.4.1
* django-rules-0.2
* django-smuggler-0.2 ?
* django-mptt-0.5.2
* django-tagging-0.3.1
* BeautifulSoup-3.2.0
* html5lib-0.90
* httplib2-0.7.2
* python-openid-2.2.5
* xlrd-0.6.1
* PIL

* django-debug-toolbar-0.9.4 (optional)
* south-0.7.3 (optional)
