# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# https://bitbucket.org/schinckel/django-python-code-field/overview


#==============================================================================    
class PythonCodeWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        """
        TODO: have a syntax hilight feature, where instead of a TextArea,
        you get a div that can be double-clicked in to make it editable,
        and after leaving it re-highlights.
        """
        if value is None:
            value = ""
        if attrs is None:
            attrs = {}
        if attrs.has_key('class'):
            attrs['class'] += ' python-code'
        else:
            attrs['class'] = 'python-code'
        html = super(PythonCodeWidget, self).render(name, value, attrs=attrs)
        js = '''
   <script type="text/javascript">
     (function($){
       $(document).ready(function(){
        if ($('#_readonly_mode').length == 0) {
         var editor = CodeMirror.fromTextArea($("#id_%(name)s")[0], {
           mode: { name: "python",
                   version: 2,
                   singleLineStringErrors: false },
           lineNumbers: true,
           matchBrackets: false,
           tabMode: "shift",
           indentUnit: 4,
           theme: "cobalt",
           onChange: function(editor, changes) {
               $("#id_%(name)s").val(editor.getValue());
           }
         });
        } // _readonly_mode
       });
     }(django.jQuery));
    </script>
        ''' % dict(name=name)
        return mark_safe(u'%s\n%s' % (html, js))
    
    class Media:
        js = (
            '%scodemirror/lib/codemirror.js' % settings.STATIC_URL,
            '%scodemirror/mode/python/python.js' % settings.STATIC_URL,
        )
        css = {
            'all':(
                '%scodemirror/lib/codemirror.css' % settings.STATIC_URL,
                '%scodemirror/theme/cobalt.css' % settings.STATIC_URL,
            )
        }


#==============================================================================    
class PythonCodeFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = PythonCodeWidget
        super(PythonCodeFormField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        """
        We need to ensure that the code that was entered validates as
        python code.
        """
        
        if not value:
            return
        
        if isinstance(value, basestring):
            try:
                value = value.replace('\r', '')
                compile(value, "<string>", 'exec')
            except SyntaxError, arg:
                raise forms.ValidationError(u'Syntax Error: %s' % unicode(arg))
            return value


#==============================================================================    
class PythonCodeField(models.TextField):
    """
    A field that will ensure that data that is entered into it is syntactically
    valid python code.
    """
    
    __metaclass__ = models.SubfieldBase
    description = "Python Source Code"
    
    def formfield(self, **kwargs):
        return super(PythonCodeField, self).formfield(form_class=PythonCodeFormField, **kwargs)

    @staticmethod
    def evaluate(code):
        if isinstance(code, basestring):
            try:
                code = code.replace('\r', '')
                compiled_code = compile(code, "<string>", 'exec')
                retval = {}
                exec compiled_code in retval
                return retval
            except SyntaxError, arg:
                pass
        return None


#==============================================================================    
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^python_field\.fields\.PythonCodeField'])
except ImportError:
    pass