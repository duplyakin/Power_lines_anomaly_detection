from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from analyse.models import Region, Lep, Photo, Pole
from lep import constants
from django.utils.translation import gettext_lazy as _
from django.db import connections

from analyse.models import *


@login_required
def index_dashboard(request):

    # with connections['devlabs_db'].cursor() as cursor:
    #     cursor.execute("SELECT * FROM tasks WHERE id = %s", [photo.task_id])
    #     # cursor.execute("SELECT * FROM tasks WHERE id = 1")
    #     row = cursor.fetchone()
    #     result_link = str(row[3])
    #     line_broken = row[4]
    #     vibration_damper_displacement = row[5]
    #     garland_problem = row[6]
    #     print(type(row))
    #     print(row[0])
    #     print(row[3])
    #     print(row[4])
    #     print(row[5])
    #     print(row[6])
    #     print(type(row[6]))

    regions = Region.objects.filter(is_active=True)
    leps = Lep.objects.all()
    poles = Pole.objects.all()
    photos = Photo.objects.all()

    context = {
        'photos': photos,
        'regions': regions,
        'leps': leps,
        'poles': poles,
        'navbar': constants.NAVBAR_INDEX_DASHBOARD,
    }
    return render(request, 'dashboard/index.html', context=context)
