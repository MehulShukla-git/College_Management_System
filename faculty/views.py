from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone

from .models import Faculty
from .forms import AssignmentForm
from students.models import Student, Enrollment
from courses.models import Course, Assignment
from attendance.models import Attendance

@login_required(login_url='users:login')
def faculty_dashboard(request):
    faculty = Faculty.objects.filter(user=request.user).first()
    if not faculty:
        faculty = None  # For non-faculty, show empty dashboard
    # Courses assigned to this faculty (Course.faculty is ManyToManyField to Faculty)
    courses_assigned = Course.objects.filter(faculty=faculty) if faculty else []
    assignments = Assignment.objects.filter(faculty=faculty).order_by('-created_at') if faculty else []
    form = AssignmentForm()
    if faculty:
        form.fields['course'].queryset = courses_assigned
    context = {
        'faculty': faculty,
        'courses': courses_assigned,
        'assignments': assignments,
        'form': form,
    }
    return render(request, 'faculty/dashboard.html', context)

@login_required(login_url='users:login')
def mark_attendance(request, course_id):
    faculty = Faculty.objects.filter(user=request.user).first()
    if not faculty:
        return HttpResponseForbidden("You need a faculty profile to mark attendance.")
    course = get_object_or_404(Course, id=course_id)

    # ensure this faculty is assigned to the course
    if not course.faculty.filter(id=faculty.id).exists():
        return HttpResponseForbidden("You are not assigned to this course.")

    # Get enrollments for this course and faculty
    enrollments = Enrollment.objects.filter(course=course, faculty=faculty)
    students = [enrollment.student for enrollment in enrollments]

    if request.method == 'POST':
        # get chosen date or default to today
        date_str = request.POST.get('date')
        try:
            if date_str:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                selected_date = timezone.now().date()
        except Exception:
            selected_date = timezone.now().date()

        present_ids = request.POST.getlist('present')  # list of student ids marked as present

        # create or update attendance entries
        for enrollment in enrollments:
            status = 'Present' if str(enrollment.student.id) in present_ids else 'Absent'
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=selected_date,
                defaults={'status': status}
            )

        messages.success(request, f"Attendance saved for {course.name} on {selected_date}.")
        return redirect('faculty:dashboard')

    # GET: show form
    today = timezone.now().date().strftime('%Y-%m-%d')
    context = {'course': course, 'enrollments': enrollments, 'today': today}
    return render(request, 'faculty/mark_attendance.html', context)

@login_required(login_url='users:login')
def view_attendance(request, course_id):
    faculty = Faculty.objects.filter(user=request.user).first()
    if not faculty:
        faculty = None
    course = get_object_or_404(Course, id=course_id)
    if faculty and not course.faculty.filter(id=faculty.id).exists():
        return HttpResponseForbidden("You are not assigned to this course.")

    enrollments = Enrollment.objects.filter(course=course, faculty=faculty) if faculty else Enrollment.objects.filter(course=course)
    attendances = Attendance.objects.filter(enrollment__in=enrollments).select_related('enrollment__student').order_by('-date')
    context = {'course': course, 'enrollments': enrollments, 'attendances': attendances}
    return render(request, 'faculty/view_attendance.html', context)

@login_required(login_url='users:login')
def view_student_attendance(request, student_id):
    # anyone can view a student's attendance records
    student = get_object_or_404(Student, id=student_id)
    enrollments = student.enrollments.all()
    records = Attendance.objects.filter(enrollment__in=enrollments).select_related('enrollment').order_by('-date')
    context = {'student': student, 'records': records, 'enrollments': enrollments}
    return render(request, 'faculty/student_attendance.html', context)

@login_required(login_url='users:login')
def create_assignment(request):
    faculty = Faculty.objects.filter(user=request.user).first()
    if not faculty:
        messages.error(request, "You need a faculty profile to create assignments.")
        return redirect('faculty:dashboard')

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.faculty = faculty
            assignment.save()
            messages.success(request, f"Assignment '{assignment.title}' created.")
            return redirect('faculty:dashboard')
    else:
        form = AssignmentForm()
        # Limit course choices to those assigned to this faculty
        form.fields['course'].queryset = Course.objects.filter(faculty=faculty)

    context = {'form': form}
    return render(request, 'faculty/create_assignment.html', context)
