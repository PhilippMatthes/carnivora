import json
import operator
import os
import subprocess

from django.shortcuts import render, render_to_response
from django.utils.datastructures import MultiValueDictKeyError

from carnivora.instabot.config import ConfigLoader
from carnivora.instabot.log import Log
from carnivora.instabot.statistics import Statistics
from tf_open_nsfw.classify_nsfw import classify_nsfw

page_size = 20


def index(request):
    return render_to_response('index.html')


def update_server(request):
    commands = [["git", "status"], ["git", "pull"]]
    output = []
    for command in commands:
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        output.append(
            (" ".join(command), process.stdout, str(process.wait(timeout=30)))
        )
    return render(request, 'server_update.html', {'output': output})


def table_monitor_update(request):
    # pages = range(Log.number_of_pages(page_size=page_size))
    try:
        search = request.GET['search']
    except MultiValueDictKeyError as e:
        print(e)
        search = ''
    lines = Log.get(page_size, search=search)
    return render(request, 'table_monitor_update.html', {'lines': lines})


def submit_to_config(request):
    try:
        config_key = request.GET['config_key']
        config_param = request.GET['config_param']
        ConfigLoader.store(config_key, config_param)
    except MultiValueDictKeyError as e:
        print(e)
    return render(request, 'settings_update.html', {'config_key': config_key, 'config_param': config_param})


def monitor(request):
    # pages = range(Log.number_of_pages(page_size=page_size))
    lines = Log.get(page_size)
    return render(request, 'monitor.html', {'lines': lines})


def statistics(request):
    hashtag_names, hashtag_scores = Statistics.get_hashtags(n=40, truncated_name_length=20)
    amount_of_users, amount_of_interactions, amount_of_likes, amount_of_follows, amount_of_comments\
        = Statistics.get_amount_of_actions()
    amount_of_follows_all_time = Statistics.get_amount_of_followed_accounts()
    render_data = {
        'hashtag_names': json.dumps(hashtag_names),
        'hashtag_scores': hashtag_scores,
        'amount_of_users': amount_of_users,
        'amount_of_likes': amount_of_likes,
        'amount_of_comments': amount_of_comments,
        'amount_of_follows': amount_of_follows,
        'amount_of_interactions': amount_of_interactions,
        'amount_of_follows_all_time': amount_of_follows_all_time,
    }
    return render(request, 'statistics.html', render_data)


def submit_nsfw(request):
    try:
        link = request.GET['nsfw_link']
        sfw, nsfw = classify_nsfw(link)
        return render(request, 'nsfw_progress_bar.html', {'nsfw': nsfw})
    except MultiValueDictKeyError as e:
        print(e)
        return render(request, 'nsfw_progress_bar.html', {'nsfw': 0.0})


def server(request):
    return render(request, 'server.html')


def nsfw_check(request):
    return render(request, 'nsfw_check.html')


def perform_reboot(request):
    os.system('sudo reboot now')


def settings(request):
    config = ConfigLoader.load()
    sorted_config = sorted(config.items(), key=operator.itemgetter(0))
    return render(request, 'settings.html', {'sorted_config': sorted_config})
