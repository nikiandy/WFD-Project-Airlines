from django.urls import path
from . import views

app_name = 'bookings'

# URL patterns for this app
urlpatterns = [
    path('', views.index, name='index'),

# URL for new
path('new/', views.booking_create, name='booking_create'),

# URL for <str:reference_number>
path('<str:reference_number>/', views.booking_detail, name='booking_detail'),

# URL for <str:reference_number>/edit
path('<str:reference_number>/edit/', views.booking_edit, name='booking_edit'),

# URL for <str:reference_number>/cancel
path('<str:reference_number>/cancel/', views.booking_cancel, name='booking_cancel'),

# URL for <str:reference_number>/payment
path('<str:reference_number>/payment/', views.booking_payment, name='booking_payment'),

# URL for api/search-flights
path('api/search-flights/', views.api_search_flights, name='api_search_flights'),

# URL for <str:booking_reference>/services
path('<str:booking_reference>/services/', views.manage_additional_services, name='manage_services'),
] 