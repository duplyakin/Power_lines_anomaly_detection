"""lep URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from account import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('analyse/', include('analyse.urls')),
    path('dashboard/', include('dashboard.urls')),
    # path('room/', include('room.urls')),
    # path('event/', include('event.urls')),
    path('register/', user_views.register, name='register_url'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login_url'),
    path('logout/', auth_views.LogoutView.as_view(template_name='account/logout.html'), name='logout_url'),
    path('', user_views.main_page, name='main_page_url'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
