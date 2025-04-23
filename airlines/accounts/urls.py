from django.urls import path
from . import views

app_name = 'accounts'

# URL patterns for this app
urlpatterns = [
    path('', views.index, name='index'),

# URL for login
path('login/', views.login_view, name='login'),

# URL for signup
path('signup/', views.signup_view, name='signup'),

# URL for logout
path('logout/', views.logout_view, name='logout'),

# URL for password-reset
path('password-reset/', views.password_reset, name='password_reset'),

# URL for profile
path('profile/', views.profile, name='profile'),

# URL for profile/edit
path('profile/edit/', views.edit_profile, name='edit_profile'),

# URL for staff/create
path('staff/create/', views.create_staff_account, name='create_staff'),
] 