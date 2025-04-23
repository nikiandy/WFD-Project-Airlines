from django.shortcuts import render
from django.http import HttpResponse

def home(

    return render(request, 'home.html', {
        'title': 'Welcome to Airlines Booking System'
    })

def handler404(

    return render(request, '404.html', status=404)

def handler500(

    return render(request, '500.html', status=500) 