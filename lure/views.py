from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response


# Create your views here.
from instabot.log import Log


def index(request):
    return render_to_response('index.html')


def table_monitor_update(request):
    lines = Log.get()
    return render(request, 'table_monitor_update.html', {'lines': lines})
