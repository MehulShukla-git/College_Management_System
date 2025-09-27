from django.contrib import admin
from .models import Student, Enrollment

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_no', 'fees_status')
    search_fields = ('user__username', 'roll_no')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'faculty', 'enrolled_at')
    list_filter = ('course', 'faculty')
    search_fields = ('student__user__username', 'course__name')
