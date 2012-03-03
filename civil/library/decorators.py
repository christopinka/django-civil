# -*- coding: utf-8 -*-

from functools import wraps

#==============================================================================
def unique_boolean(field):
    """
    Allows to specify a unique boolean for a model.
    """
    def factory(func):
        @wraps(func)
        def decorator(self):
            if getattr(self, field):
                try:
                    tmp = self.__class__.objects.get(**{ field: True })
                    if self != tmp:
                        setattr(tmp, field, False)
                        tmp.save()
                except self.__class__.DoesNotExist:
                    if getattr(self, field) != True:
                        setattr(self, field, True)
            return func(self)
        return decorator
    return factory


#==============================================================================
def unique_boolean_for_instance(field, instance):
    """
    Allows to specify a unique boolean for an object, and keep that boolean
    unique for a set of common instances that share the same field.
    """
    def factory(func):
        @wraps(func)
        def decorator(self):
            if getattr(self, field) and getattr(self, instance):
                try:
                    tmp = self.__class__.objects.get(**{ instance: getattr(self, instance), field: True })
                    if self != tmp:
                        setattr(tmp, field, False)
                        tmp.save()
                except self.__class__.DoesNotExist:
                    if getattr(self, field) != True:
                        setattr(self, field, True)
            return func(self)
        return decorator
    return factory


#==============================================================================
def autoconnect(cls):
    """ 
    Class decorator that automatically connects pre_save / post_save signals on 
    a model class to its pre_save() / post_save() methods.
    """
    def connect(signal, func):
        cls.func = staticmethod(func)
        @wraps(func)
        def wrapper(sender, **kwargs):
            return func(kwargs.get('instance'))
        signal.connect(wrapper, sender=cls)
        return wrapper

    from django.db.models import signals

    if hasattr(cls, 'pre_init'):
        cls.pre_init = connect(signals.pre_init, cls.pre_init)

    if hasattr(cls, 'post_init'):
        cls.post_init = connect(signals.post_init, cls.post_init)

    if hasattr(cls, 'pre_save'):
        cls.pre_save = connect(signals.pre_save, cls.pre_save)

    if hasattr(cls, 'post_save'):
        cls.post_save = connect(signals.post_save, cls.post_save)

    if hasattr(cls, 'pre_delete'):
        cls.pre_delete = connect(signals.pre_delete, cls.pre_delete)

    if hasattr(cls, 'post_delete'):
        cls.post_delete = connect(signals.post_delete, cls.post_delete)

    if hasattr(cls, 'm2m_changed'):
        cls.m2m_changed = connect(signals.m2m_changed, cls.m2m_changed)
    
    return cls
