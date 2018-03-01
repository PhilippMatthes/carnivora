from django.shortcuts import render, render_to_response
from carnivora.instabot.log import Log
from carnivora.instabot.statistics import Statistics


def index(request):
    return render_to_response('index.html')


def table_monitor_update(request):
    lines = Log.get()
    return render(request, 'table_monitor_update.html', {'lines': lines})


def monitor(request):
    return render(request, 'monitor.html')


def followed_users(request):
    return render(request, 'followed_users.html')


def hashtags(request):
    return render(request, 'hashtags.html')


def settings(request):
    return render(request, 'settings.html')


def hashtags_update(request):
    lines = Statistics.get_hashtags()
    lines_truncated = []
    for hashtag, num in lines:
        lines_truncated.append((hashtag[:20], num))
    return render(request, 'table_monitor_update.html', {'lines': lines_truncated})
