from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index_dashboard, name='index_dashboard_url'),



]
