from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """its filter getting value in dict on render template"""
    return dictionary.get(key)
