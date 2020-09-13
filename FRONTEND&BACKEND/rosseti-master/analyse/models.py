from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
from account.models import User


class Region(models.Model):
    title = models.CharField(verbose_name=_('Region name'), max_length=255, null=True)
    color = models.CharField(verbose_name=_('Color'), max_length=10, null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=1000, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return self.title


class Lep(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    title = models.CharField(verbose_name=_('Lep name'), max_length=255, null=True)
    color = models.CharField(verbose_name=_('Color'), max_length=10, null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=1000, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return self.title

class Pole(models.Model):
    lep = models.ForeignKey(Lep, on_delete=models.CASCADE, null=True)
    title = models.CharField(verbose_name=_('Pole name'), max_length=255, null=True)
    color = models.CharField(verbose_name=_('Color'), max_length=10, null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=2000, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return self.title

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    pole = models.ForeignKey(Pole, on_delete=models.CASCADE, null=True)
    original_name = models.CharField(verbose_name=_('Original name'), max_length=255, null=True, blank=True)
    generated_name = models.CharField(verbose_name=_('Generated name'), max_length=255, null=True, blank=True)
    server_name = models.CharField(verbose_name=_('Server name'), max_length=255, null=True, blank=True)
    task_id = models.IntegerField(verbose_name=_('Task ID'), null=True, blank=True)
    photo_link = models.TextField(verbose_name=_('Photo link'), max_length=1000, null=True)
    latitude = models.CharField(verbose_name=_('Latitude'), max_length=255, null=True, blank=True)
    longitude = models.CharField(verbose_name=_('Longitude'), max_length=255, null=True, blank=True)
    full_address = models.TextField(verbose_name=_('Region name'), max_length=1000, null=True)
    pole_name = models.CharField(verbose_name=_('Pole name'), max_length=255, null=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=2000, null=True, blank=True)
    image = models.ImageField(upload_to='lep_small', null=True, blank=True)
    is_sent_to_server = models.BooleanField(verbose_name=_('Is sent'), default=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), default=True)
    created_at = models.DateTimeField(verbose_name=_('Created date'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated date'), auto_now=True, null=True)

    def __str__(self):
        return str(self.original_name)
