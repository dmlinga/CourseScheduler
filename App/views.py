# from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import *
from django.shortcuts import render
# Create your views here.

def home(request):
    courses = Course.objects.all()
    sections = Section.objects.all()
    locations = Location.objects.all()

    context = {
        'courses': courses,
        'sections': sections,
        'locations': locations,
    }

    return render(request, 'home.html', context)
    



