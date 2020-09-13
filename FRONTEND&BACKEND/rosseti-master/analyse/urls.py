from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index_anylyse, name='index_analyse_url'),
    path('photo_upload', photo_upload, name='photo_upload_url'),
    path('photo_detail/<int:photo_id>', photo_detail, name='photo_detail_url'),


]
