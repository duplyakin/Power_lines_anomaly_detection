from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static


register = template.Library()


# @register.filter(name='get_full_name')
# def get_full_name(user):
#     """Get user full name"""
#     return user.first_name + ' ' + user.last_name
