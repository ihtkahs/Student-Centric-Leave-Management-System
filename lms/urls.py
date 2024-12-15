from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='login'),  # Use custom login
    path('logout/', views.logout_view, name='logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('counsellor/dashboard/', views.counsellor_dashboard, name='counsellor_dashboard'),
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('apply/leave/', views.apply_leave, name='apply_leave'),
    path('my/profile/', views.my_profile, name='my_profile'),
    path('counsellor/approve/leave', views.counsellor_approve_leave, name='counsellor_approve_leave'),
]
