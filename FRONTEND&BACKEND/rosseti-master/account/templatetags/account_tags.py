from django import template
from django.contrib.auth.models import Group, Permission
from django.contrib.staticfiles.templatetags.staticfiles import static


register = template.Library()


@register.filter(name='get_full_name')
def get_full_name(user):
    """Get user full name"""
    return user.first_name + ' ' + user.last_name


@register.filter(name='get_user_image')
def get_user_image(user):
    """Check if user has group"""

    if user.profile.image:
        return user.profile.image.url
    elif user.gender == 0:
        return static('images/account/man.svg')
    elif user.gender == 1:
        return static('images/account/woman.svg')
    else:
        return static('images/account/other.png')

@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user has group"""
    return user.groups.filter(name=group_name).exists()


@register.filter(name='has_permission')
def has_permission(user, permission_name):
    """Check if user has permission"""
    # Individual permissions
    return Permission.objects.filter(user=user, codename=permission_name).exists()


@register.filter(name='has_perm_in_group')
def has_perm_in_group(user, permission_name):
    """Check permission in group for current user"""
    # Permissions that the user has via a group
    # group_permissions = Permission.objects.filter(group__user=user)
    return Permission.objects.filter(group__user=user, codename=permission_name).exists()


@register.filter(name='has_perm_in_group_or_perm')
def has_perm_in_group_or_perm(user, permission_name):
    """Check permission in group table and in permission table for current user"""
    if Permission.objects.filter(group__user=user, codename=permission_name).exists():
        return True

    if Permission.objects.filter(user=user, codename=permission_name).exists():
        return True

    return False
