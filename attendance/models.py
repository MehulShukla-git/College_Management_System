from django.db import models
from students.models import Enrollment

class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=(("Present","Present"), ("Absent","Absent")))

    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.enrollment.course.name} - {self.date} - {self.status}"
