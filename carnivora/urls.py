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
    url(r'^register_user/$', views.register_user, name='register_user'),
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
    url(r'^run_instabot/$', views.run_instabot, name="run_instabot"),
    url(r'^stop_instabot/$', views.stop_instabot, name="stop_instabot"),
    url(r'^load_button_chain/$', views.load_button_chain, name="load_button_chain"),
    url(r'^load_registration/$', views.load_registration, name="load_registration"),
    url(r'^logout_user/$', views.logout_user, name="logout_user"),
    url(r'^load_screenshot/$', views.load_screenshot, name="load_screenshot"),
    url(r'^submit_to_classification/$', views.submit_to_classification, name="submit_to_classification"),

]
