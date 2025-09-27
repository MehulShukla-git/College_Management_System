from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('enroll/', views.enroll_course, name='enroll'),
    # add attendance, profile, etc...
]
