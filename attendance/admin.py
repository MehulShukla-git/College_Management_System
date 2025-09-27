from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('enrollment__student__user__username',)

    def enrollment(self, obj):
        return f"{obj.enrollment.student.user.username} - {obj.enrollment.course.name} - {obj.enrollment.faculty}"
    enrollment.short_description = 'Enrollment Details'
