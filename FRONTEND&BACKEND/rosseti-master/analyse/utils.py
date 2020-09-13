import uuid
from geopy.geocoders import Nominatim

from analyse.models import Region, Pole, Lep, Photo


def generate_random_name(filename):
    uuid.uuid1()


def get_pole_name(filename):
    split_name = filename.split('.')
    return str(split_name[1][0:3])


def get_latitude(filename):
    split_name = filename.split('_')
    return str(split_name[2][2:])


def get_longitude(filename):
    split_name = filename.split('_')
    return str(split_name[3][2:])


def get_region(latitude, longitude):
    geolocator = Nominatim(user_agent="rosseti")
    location = geolocator.reverse(latitude + ', ' + longitude)
    location_string = location.address
    location_arr = location_string.split(', ')
    for loc in location_arr:
        if 'область' in loc:
            return loc

    return str(location_arr[2])


def get_full_address(latitude, longitude):
    geolocator = Nominatim(user_agent="rosseti")
    location = geolocator.reverse(latitude + ', ' + longitude)
    return str(location.address)


# Check if Region exists
def check_region_exist(region):
    try:
        region = Region.objects.get(title__exact=region)
        return region.id
    except Region.DoesNotExist:
        return False


def get_region_id(region):
    if check_region_exist(region):
        return check_region_exist(region)
    else:
        new_region = Region(title=region)
        new_region.save()
        return new_region.id


# Check if LEP exists
def check_lep_exist(lep, region_id):
    try:
        lep = Lep.objects.get(title__exact=lep, region=region_id)
        return lep.id
    except Lep.DoesNotExist:
        return False


def get_lep_id(lep, region_id):
    if check_lep_exist(lep, region_id):
        return check_lep_exist(lep, region_id)
    else:
        new_lep = Lep(title=lep, region_id=region_id)
        new_lep.save()
        return new_lep.id


# Check if Pole exists
def check_pole_exist(pole, lep_id):
    try:
        pole = Pole.objects.get(title__exact=pole, lep=lep_id)
        return pole.id
    except Pole.DoesNotExist:
        return False


def get_pole_id(pole, lep_id):
    if check_pole_exist(pole, lep_id):
        return check_pole_exist(pole, lep_id)
    else:
        new_pole = Pole(title=pole, lep_id=lep_id)
        new_pole.save()
        return new_pole.id


def check_photo_exists(filename):
    try:
        photo = Photo.objects.get(original_name__exact=filename)
        return photo.id
    except Photo.DoesNotExist:
        return False


# def save_photo_to_db(user_id, pole_id, filename, original_name, server_name)


# print(get_pole_name('image_00564294_lt52.68431159_ln39.61779539_p-617_r00_y1315.jpg'))
# print(get_latitude('image_00564294_lt52.68431159_ln39.61779539_p-617_r00_y1315.jpg'))
# print(get_longitude('image_00564294_lt52.68431159_ln39.61779539_p-617_r00_y1315.jpg'))
# print(get_region('52.69191180', '39.62685296'))
# print(get_full_address('52.69191180', '39.62685296'))


