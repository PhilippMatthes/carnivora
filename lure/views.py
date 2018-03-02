import json

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
    hashtags = Statistics.get_hashtags()
    hashtag_names = []
    hashtag_scores = []
    for hashtag_name, hashtag_score in hashtags[:20]:
        hashtag_names.append(hashtag_name[:20])
        hashtag_scores.append(hashtag_score)
    return render(request, 'hashtags.html', {'hashtag_names': json.dumps(hashtag_names), 'hashtag_scores': hashtag_scores})


def settings(request):
    return render(request, 'settings.html')
