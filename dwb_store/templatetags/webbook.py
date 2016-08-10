from django import template

register = template.Library()

@register.filter(name='price')
def price(value):
    return "$ %.2f USD" % (value,)