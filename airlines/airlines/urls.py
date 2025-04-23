
from django.contrib import admin
from django.urls import path, include
from . import views

# URL patterns for this app
urlpatterns = [
    path('', views.home, name='home'),  

# URL for admin
path('admin/', admin.site.urls),

# URL for accounts
path('accounts/', include('accounts.urls')),

# URL for flights
path('flights/', include('flights.urls')),

# URL for bookings
path('bookings/', include('bookings.urls')),

# URL for crew
path('crew/', include('crew.urls')),

# URL for passengers
path('passengers/', include('passengers.urls')),
]

handler404 = 'airlines.views.handler404'
handler500 = 'airlines.views.handler500'
