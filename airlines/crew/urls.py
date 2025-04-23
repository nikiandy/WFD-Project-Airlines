from django.urls import path
from . import views

app_name = 'crew'

# URL patterns for this app
urlpatterns = [

    path('', views.index, name='index'),

# URL for dashboard
path('dashboard/', views.crew_dashboard, name='crew_dashboard'),

# URL for schedules
path('schedules/', views.schedule_list, name='crew_schedule_list'),

# URL for schedules/<int:pk>
path('schedules/<int:pk>/', views.schedule_detail, name='crew_schedule_detail'),

# URL for schedules/<int:pk>/check-in
path('schedules/<int:pk>/check-in/', views.schedule_check_in, name='crew_schedule_check_in'),

# URL for schedules/<int:pk>/check-out
path('schedules/<int:pk>/check-out/', views.schedule_check_out, name='crew_schedule_check_out'),

# URL for qualifications
path('qualifications/', views.qualification_list, name='crew_qualification_list'),

# URL for leaves
path('leaves/', views.leave_list, name='crew_leave_list'),

# URL for leaves/request
path('leaves/request/', views.leave_request, name='crew_leave_request'),

# URL for management/leaves/approval
path('management/leaves/approval/', views.leave_approval, name='crew_leave_approval'),

# URL for management/crew
path('management/crew/', views.crew_list, name='crew_list'),
] 