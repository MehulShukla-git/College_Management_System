from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django import forms
from django.db.models import Count, Q
from .models import CustomUser
from courses.models import Course, Assignment
from students.models import Student, Enrollment
from faculty.models import Faculty
from attendance.models import Attendance

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), label='Role')

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role',)

def home(request):
    if not request.user.is_authenticated:
        return redirect('users:login')
    courses = Course.objects.all()

    # Get enrolled courses for student dashboard
    enrolled_courses = []
    if hasattr(request.user, 'student'):
        enrolled_courses = [e.course for e in Enrollment.objects.filter(student=request.user.student)]

    # Get assigned courses for faculty dashboard
    assigned_courses = []
    if hasattr(request.user, 'faculty'):
        assigned_courses = Course.objects.filter(faculty=request.user.faculty)

    # Calculate performance data for all students and faculty
    students_performance = []
    total_student_present = 0
    total_student_absent = 0
    for student in Student.objects.all():
        enrollments = Enrollment.objects.filter(student=student)
        total_attendance = Attendance.objects.filter(enrollment__in=enrollments).count()
        present_attendance = Attendance.objects.filter(enrollment__in=enrollments, status='Present').count()
        absent_attendance = total_attendance - present_attendance
        attendance_pct = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
        # Mock result score based on attendance for now
        result_score = attendance_pct  # Can integrate with exams later
        students_performance.append({
            'student': student,
            'attendance_pct': round(attendance_pct, 2),
            'result_score': round(result_score, 2),
            'present': present_attendance,
            'total': total_attendance
        })
        total_student_present += present_attendance
        total_student_absent += absent_attendance

    faculty_performance = []
    total_faculty_present = 0
    total_faculty_absent = 0
    for faculty in Faculty.objects.all():
        courses = Course.objects.filter(faculty=faculty)
        enrollments = Enrollment.objects.filter(course__in=courses, faculty=faculty)
        total_attendance = Attendance.objects.filter(enrollment__in=enrollments).count()
        present_attendance = Attendance.objects.filter(enrollment__in=enrollments, status='Present').count()
        absent_attendance = total_attendance - present_attendance
        attendance_pct = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
        # Mock performance score for faculty (e.g., average student attendance)
        faculty_performance.append({
            'faculty': faculty,
            'attendance_pct': round(attendance_pct, 2),
            'total_students': enrollments.values('student').distinct().count(),
            'present': present_attendance,
            'total': total_attendance
        })
        total_faculty_present += present_attendance
        total_faculty_absent += absent_attendance

    context = {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
        'assigned_courses': assigned_courses,
        'user_role': request.user.role if request.user.is_authenticated else None,
        'students_performance': students_performance,
        'faculty_performance': faculty_performance,
        'total_student_present': total_student_present,
        'total_student_absent': total_student_absent,
        'total_faculty_present': total_faculty_present,
        'total_faculty_absent': total_faculty_absent,
    }
    return render(request, 'users/home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('users:dashboard_redirect')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def dashboard_redirect(request):
    if request.user.is_authenticated:
        return redirect('users:home')  # Redirect to home with all tabs
    return redirect('users:home')

def admin_dashboard(request):
    all_users = CustomUser.objects.all()
    all_courses = Course.objects.all()
    all_students = Student.objects.all()
    all_faculty = Faculty.objects.all()
    all_assignments = Assignment.objects.all()
    all_enrollments = Enrollment.objects.all()
    attendance_summary = Attendance.objects.values('enrollment__course__name').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='Present')),
        absent=Count('id', filter=Q(status='Absent'))
    ).order_by('-total')
    context = {
        'all_users': all_users,
        'all_courses': all_courses,
        'all_students': all_students,
        'all_faculty': all_faculty,
        'all_assignments': all_assignments,
        'all_enrollments': all_enrollments,
        'attendance_summary': attendance_summary,
    }
    return render(request, 'admin/dashboard.html', context)
