# -*- coding: utf-8 -*-

from django.template import Node, NodeList
from django.template import TemplateSyntaxError, VariableDoesNotExist
from django.template import Library
import re

register = Library()
variable_re = re.compile(r'[\w._\|\"\']+')
string_re = re.compile(r'^([\"\']).*\1$')

TAGNAME = 'pyif' # Hopefully this can replace django's built-in if tag

class IfNode(Node):
    def __init__(self, expression, variables, nodelist_true, nodelist_false):
        self.expression = expression
        self.variables = variables
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def __repr__(self):
        return "<If node>"

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def get_nodes_by_type(self, nodetype):
        nodes = []
        if isinstance(self, nodetype):
            nodes.append(self)
        nodes.extend(self.nodelist_true.get_nodes_by_type(nodetype))
        nodes.extend(self.nodelist_false.get_nodes_by_type(nodetype))
        return nodes

    def render(self, context):
        variable_context = {}
        expression = self.expression
        for variable in self.variables:
            try:
                value = variable.resolve(context, True)
            except VariableDoesNotExist:
                value = None

            context_name = 'var%s' % len(variable_context)
            expression = re.sub(r'(?<![\w._\|])%s(?![\w._\|])' % re.escape(variable.token), context_name, expression)
            variable_context[context_name] = value
        try:
            resultant = eval(expression, variable_context)
        except:
            resultant = False

        if not resultant:
            return self.nodelist_false.render(context)
        return self.nodelist_true.render(context)

def do_if(parser, token):
    """
    Template tag {% pyif %}

    Supports:
       1. ==, !=
       2. not ....
       3. v in (1,"y",z)
       4. <=, <, >=, >
       5. nesting (True and (False or (True or False)))

    How to use it:

        {% pyif i == 1 or (5 >= i and i != 7) and user.first_name in ('John', 'Jacob') %}
        {% else %}
        {% endif %} 
    
    """
    bits = token.contents.split(None, 1)
    if len(bits) != 2:
        raise TemplateSyntaxError, "'%' statement requires at least one argument" % TAGNAME
    expression = bits[1]
    variables = set([ parser.compile_filter(x) for x in variable_re.findall(expression) if x not in ('and', 'or', 'not', 'in') and not string_re.match(x) ])
    nodelist_true = parser.parse(('else', 'endif'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    return IfNode(expression, variables, nodelist_true, nodelist_false)

do_if = register.tag(TAGNAME, do_if)
