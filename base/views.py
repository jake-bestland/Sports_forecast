import json

from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import HttpResponse
from rest_framework.response import Response


# my first demo view
@api_view(['GET'])
def hello(request):
    # return hello world
    return HttpResponse("Hello World")

# create dashboard view
@api_view(['GET'])
def dashboard(request):
    # read from base/datafactory/data/output/extracted.json
    read_path = 'base/datafactory/data/output/extracted.json'
    with open(read_path, 'r') as f:
        data = json.load(f)
    return Response(data)
