from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response


# Create your views here.


def index(request):
    return render_to_response('index.html')


def get_more_tables(request):
    increment = int(request.GET['append_increment'])
    increment_to = increment + 10
    lines = range(increment_to)
    print(increment)
    return render(request, 'get_more_tables.html', {'lines': lines})
