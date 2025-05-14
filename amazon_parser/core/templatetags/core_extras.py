import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def pprint(value):
    """Pretty prints JSON data"""
    try:
        formatted_json = json.dumps(value, indent=2)
        return mark_safe(formatted_json)
    except:
        return value
