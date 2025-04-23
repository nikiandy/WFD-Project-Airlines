from django.urls import path
from . import views

app_name = 'passengers'

# URL patterns for this app
urlpatterns = [
    path('', views.index, name='index'),
] 