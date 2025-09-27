from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('dashboard/', views.faculty_dashboard, name='dashboard'),
    path('mark-attendance/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('student-attendance/<int:student_id>/', views.view_student_attendance, name='view_student_attendance'),
    path('create-assignment/', views.create_assignment, name='create_assignment'),
]
