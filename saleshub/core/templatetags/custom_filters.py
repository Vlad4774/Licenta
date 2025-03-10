from django import template

register = template.Library()

@register.filter
def is_production_page(value):
    return value.startswith('/product/') or value.startswith('/project/')

@register.filter
def get_volume(data, year):
    
    if data and year in data:
        return data[year]
    return None