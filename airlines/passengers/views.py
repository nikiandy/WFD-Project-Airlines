from django.shortcuts import render

def index(

    return render(request, 'passengers/index.html', {
        'title': 'Passenger Services'
    }) 