from django.urls import path
from . import views, views_simple

app_name = 'flights'

# URL patterns for this app
urlpatterns = [
    path('', views.index, name='index'),

# URL for flights
path('flights/', views.flight_list, name='flight_list'),

# URL for flights/<int:flight_id>
path('flights/<int:flight_id>/', views.flight_detail, name='flight_detail'),

# URL for status
path('status/', views.flight_status, name='flight_status'),

# URL for aircraft
path('aircraft/', views.aircraft_list, name='aircraft_list'),

# URL for aircraft/<int:aircraft_id>
path('aircraft/<int:aircraft_id>/', views.aircraft_detail, name='aircraft_detail'),

# URL for search
path('search/', views.flight_search, name='flight_search'),

# URL for generate
path('generate/', views.generate_flights, name='generate_flights'),

# URL for management
path('management/', views.flight_management, name='flight_management'),

# URL for flights/create
path('flights/create/', views.flight_create, name='flight_create'),

# URL for flights/<int:flight_id>/update
path('flights/<int:flight_id>/update/', views.flight_update, name='flight_update'),

# URL for flights/<int:flight_id>/delete
path('flights/<int:flight_id>/delete/', views.flight_delete, name='flight_delete'),

# URL for simple
path('simple/', views_simple.simple_flight_management, name='simple_flight_management'),

# URL for simple/create
path('simple/create/', views_simple.simple_flight_create, name='simple_flight_create'),

# URL for simple/update/<int:flight_id>
path('simple/update/<int:flight_id>/', views_simple.simple_flight_update, name='simple_flight_update'),

# URL for simple/delete/<int:flight_id>
path('simple/delete/<int:flight_id>/', views_simple.simple_flight_delete, name='simple_flight_delete'),
] 