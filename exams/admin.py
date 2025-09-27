from django.contrib import admin
from .models import Exam, Result

admin.site.register(Exam)
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks', 'grade')
    search_fields = ('student__user__username',)
