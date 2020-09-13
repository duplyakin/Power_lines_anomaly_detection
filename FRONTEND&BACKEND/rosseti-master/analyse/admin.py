from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Region, Lep, Pole, Photo


admin.site.register(Region)
admin.site.register(Lep)
admin.site.register(Pole)
admin.site.register(Photo)
