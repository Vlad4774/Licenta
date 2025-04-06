from django import template

register = template.Library()

@register.filter
def is_unregistred_page(path):
    return path in ['/', '/login/', '/register/']