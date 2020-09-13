from django.urls import path, include
from .views import *

urlpatterns = [
    path('', user_account, name='user_account_url'),
    path('profile/', profile, name='profile_url'),

]
