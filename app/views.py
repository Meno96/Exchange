from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import random


def homePageView(request):
    return JsonResponse('', safe=False)

def orderView(request):
    return JsonResponse('', safe=False)