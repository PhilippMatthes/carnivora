import json
import operator
import os

from django.shortcuts import render, render_to_response

from carnivora.instabot.config import ConfigLoader
from carnivora.instabot.log import Log
from carnivora.instabot.statistics import Statistics


def index(request):
    return render_to_response('index.html')


def table_monitor_update(request):
    lines = Log.get(20)
    return render(request, 'table_monitor_update.html', {'lines': lines})


def submit_to_config(request):
    config_key = request.GET['config_key']
    config_param = request.GET['config_param']
    ConfigLoader.store(config_key, config_param)
    return render(request, 'settings_update.html', {'config_key': config_key, 'config_param': config_param})


def monitor(request):
    lines = Log.get(20)
    return render(request, 'monitor.html', {'lines': lines})


def statistics(request):
    hashtags = Statistics.get_hashtags()
    hashtag_names = []
    hashtag_scores = []
    for hashtag_name, hashtag_score in hashtags[:40]:
        hashtag_names.append(hashtag_name[:40])
        hashtag_scores.append(hashtag_score)
    render_data = {
        'hashtag_names': json.dumps(hashtag_names),
        'hashtag_scores': hashtag_scores,
    }
    return render(request, 'statistics.html', render_data)


def reboot(request):
    return render(request, 'reboot.html')


def perform_reboot(request):
    os.system('sudo reboot now')


def settings(request):
    config = ConfigLoader.load()
    sorted_config = sorted(config.items(), key=operator.itemgetter(0))
    return render(request, 'settings.html', {'sorted_config': sorted_config})
