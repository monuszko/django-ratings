from django import template
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.filter(is_safe=True)
def get_forms(obj, user):
    """{% object|get_form user %}"""
    try:
        current_user = User.objects.get(username=user)
    except ObjectDoesNotExist:
        return ''
    return obj.get_forms(current_user)
