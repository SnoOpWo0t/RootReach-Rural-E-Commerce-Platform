from django import template

register = template.Library()

@register.filter
def dict_lookup(dictionary, key):
    """
    Lookup a value in a dictionary
    Usage: {{ dict|dict_lookup:key }}
    """
    if isinstance(dictionary, dict) and key in dictionary:
        return dictionary[key]
    return None

@register.filter
def percentage(value, total):
    """
    Calculate percentage: (value / total) * 100
    Usage: {{ value|percentage:total }}
    """
    try:
        if int(total) == 0:
            return 0
        return round((int(value) / int(total)) * 100, 2)
    except (ValueError, TypeError):
        return 0
