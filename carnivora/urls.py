"""carnivora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url

from lure.views import index
from django.contrib.auth import views as auth_views

import lure.views as views

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^main_body/$', views.main_body, name='main_body'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^table_monitor_update/$', views.table_monitor_update, name="table_monitor_update"),
    url(r'^submit_to_config/$', views.submit_to_config, name="submit_to_config"),
    url(r'^server/$', views.server, name="server"),
    url(r'^perform_reboot/$', views.perform_reboot, name="perform_reboot"),
    url(r'^monitor/$', views.monitor, name="monitor"),
    url(r'^statistics/$', views.statistics, name="statistics"),
    url(r'^settings/$', views.settings, name="settings"),
    url(r'^nsfw-check/$', views.nsfw_check, name="nsfw-check"),
    url(r'^submit_to_nsfw/$', views.submit_nsfw, name="submit_to_nsfw"),
    url(r'^update_server/$', views.update_server, name="update_server"),
]
