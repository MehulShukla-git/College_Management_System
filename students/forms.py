from django import forms
from .models import Enrollment
from courses.models import Course
from faculty.models import Faculty

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course', 'faculty']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        if student:
            # Get available courses and faculties
            enrolled = Enrollment.objects.filter(student=student).values_list('course_id', 'faculty_id')
            self.fields['course'].queryset = Course.objects.exclude(id__in=[e[0] for e in enrolled])
            self.fields['faculty'].queryset = Faculty.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        faculty = cleaned_data.get('faculty')
        if course and faculty:
            # Check if faculty teaches the course
            if not course.faculty.filter(id=faculty.id).exists():
                raise forms.ValidationError("Selected faculty does not teach this course.")
        return cleaned_data
