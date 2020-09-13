from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from analyse.models import Region, Lep, Photo, Pole
from lep import constants
from django.utils.translation import gettext_lazy as _
# import requests as rqvst
from django.core.files.storage import FileSystemStorage
from lep.settings import *
# from poster.streaminghttp import register_openers
# from poster.encode import multipart_encode
# import urllib2
import requests
from geopy.exc import GeocoderTimedOut
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from .utils import *
import json
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.db import connections


def index_anylyse(request):
    # declare an empty list to store
    # latitude and longitude of values
    # of city column
    longitude = []
    latitude = []

    geolocator = Nominatim(user_agent="rosseti")
    location = geolocator.reverse("52.69191180, 39.62685296")
    print('+++++++++++++++++++++')
    print(location)
    print(location.address)
    location_string = location.address
    print(type(location_string))
    location_arr = location_string.split(', ')
    print(location_arr[2])
    print('+++++++++++++++++++++')

    # locator = Nominatim(user_agent="myGeocoder")
    # coordinates = "52.69191180 39.62685296"
    # location = locator.reverse(coordinates)
    # location.raw

    regions = Region.objects.filter(is_active=True)
    leps = Lep.objects.all()
    poles = Pole.objects.all()
    photos = Photo.objects.all()
    for region in regions:
        print(region)

    context = {
        'photos': photos,
        'regions': regions,
        'leps': leps,
        'poles': poles,
        'navbar': constants.NAVBAR_MAIN,
    }
    return render(request, 'analyse/index.html', context=context)


def photo_upload(request):
    if request.method == 'POST':
        print('---------------------------')
        print(request.FILES)
        print(request.POST)
        print(request.FILES['files'])
        print(request.FILES.dict())
        fs = FileSystemStorage()
        error_existing_photos = []

        def compress(image):
            im = Image.open(image)
            size = 500, 500
            im.thumbnail(size)
            im_io = BytesIO()
            im.save(im_io, 'JPEG', quality=50)
            new_image = File(im_io, name=image.name)
            return new_image

        for img in request.FILES.getlist('files'):
            filename = fs.save('lep_images/' + img.name, img)
            filename_small = compress(img)
            filename_small_saved = fs.save('lep_small/' + img.name, filename_small)

            latitude = get_latitude(img.name)
            longitude = get_longitude(img.name)
            region_title = get_region(latitude, longitude)
            pole_full_address = get_full_address(latitude, longitude)
            lep_title = request.POST['lep_name']
            pole_title = get_pole_name(img.name)

            print('fffffffffffffffffffffffffffffff')
            print('REGION TITLE')
            print(region_title)
            print('REGION TITLE')
            region_id = get_region_id(region_title)
            lep_id = get_lep_id(lep_title, region_id)
            pole_id = get_pole_id(pole_title, lep_id)

            print(region_id)
            print(lep_id)
            print(pole_id)
            print('fffffffffffffffffffffffffffffff')
            # region_id = get_region_id(region_check)

            print('----___+++')
            print(region_title)
            print(pole_full_address)
            print(lep_title)
            print(pole_title)

            print(request.POST['lep_name'])
            print(request.POST['description'])
            print('----___+++')

            json_string = '[{"TaskId":22,"Link":"http://89.223.95.49:8888/608756232_image_000aaed2_lt52.68024562_ln39.62039965_p-621_r00_y587_cxjQCL4.jpg"}]'

            # Upload photo to Processing server
            uploaded_file_url = fs.url(filename)
            print(uploaded_file_url)
            url = 'http://89.223.95.49:8887/upload'
            print(BASE_DIR + uploaded_file_url)
            files = {'media': open(BASE_DIR + uploaded_file_url, 'rb')}
            response = requests.post(url, files=files)
            json_string = response.text
            print(json_string)
            json_data = json.loads(json_string)
            photo_link = json_data[0]['Link']
            task_id = json_data[0]['TaskId']
            file_link = str(json_data[0]['Link'])
            split_link = file_link.split('/')
            server_photo_name = split_link[-1]
            print(server_photo_name)

            photo_exists = check_photo_exists(img.name)

            if photo_exists is False:
                photo = Photo.objects.create(
                    user_id=request.user.id,
                    pole_id=pole_id,
                    original_name=img.name,
                    server_name=server_photo_name,
                    image='lep_small/' + img.name,
                    latitude=latitude,
                    longitude=longitude,
                    full_address=pole_full_address,
                    task_id=task_id,
                    photo_link=photo_link,
                    pole_name=pole_title
                )

                photo.save()

            # try:
            #
            #     # Do something with the file
            # except IOError:
            #     print("===============File not accessible")
            # finally:
            #     files.close()

        message_text = _('Photos saved successfully!')
        messages.success(request, message_text)

        return redirect('photo_upload_url')

    regions = Region.objects.filter(is_active=True)
    leps = Lep.objects.all()
    poles = Pole.objects.all()
    photos = Photo.objects.all()
    for region in regions:
        print(region)

    context = {
        'photos': photos,
        'regions': regions,
        'leps': leps,
        'poles': poles,
        'navbar': constants.NAVBAR_IMAGE_UPLOAD,
    }
    return render(request, 'analyse/image_upload.html', context=context)


@login_required
def photo_detail(request, photo_id):
    photo = Photo.objects.get(id=photo_id)
    pole_photos = Photo.objects.filter(pole_id=photo.pole_id)

    with connections['devlabs_db'].cursor() as cursor:
        cursor.execute("SELECT * FROM tasks WHERE id = %s", [photo.task_id])
        # cursor.execute("SELECT * FROM tasks WHERE id = 1")
        row = cursor.fetchone()
        result_link = str(row[3])
        line_broken = row[4]
        vibration_damper_displacement = row[5]
        garland_problem = row[6]
        print(type(row))
        print(row[0])
        print(row[3])
        print(row[4])
        print(row[5])
        print(row[6])
        print(type(row[6]))

    if request.method == 'POST':
        photo_update = Photo.objects.get(id=photo_id)
        photo_update.description = request.POST['description']
        photo_update.save()
        message_text = _('Comment was updated!')
        messages.success(request, message_text)

        return redirect('photo_detail_url', photo_id=photo_update.id)

    user_full_name = request.user.first_name + ' ' + request.user.last_name

    latitude = photo.latitude
    longitude = photo.longitude
    regions = Region.objects.filter(is_active=True)
    leps = Lep.objects.all()
    poles = Pole.objects.all()
    photos = Photo.objects.all()

    context = {
        'photos': photos,
        'regions': regions,
        'leps': leps,
        'poles': poles,
        'photo': photo,
        'latitude': latitude,
        'longitude': longitude,
        'user_full_name': user_full_name,
        'pole_photos': pole_photos,
        'result_link': result_link,
        'line_broken': line_broken,
        'status': constants.MESSAGE_STATUS_CHOICES,
        'vibration_damper_displacement': vibration_damper_displacement,
        'garland_problem': garland_problem,
        'probably': constants.STATUS_PROBABLY,
        'analise': constants.NAVBAR_INDEX_ANALYSE,
        'not_detected': constants.STATUS_NOT_DETECTED,
        'navbar': constants.NAVBAR_ROOM_LIST
    }
    return render(request, 'analyse/photo_detail.html', context=context)
