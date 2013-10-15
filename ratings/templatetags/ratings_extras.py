from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter(is_safe=True)
def get_forms(obj, user):
    """{% object|get_form user %}"""
    current_user = User.objects.get(username=user)
    return obj.get_forms(current_user)
