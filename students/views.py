from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Student, Enrollment
from .forms import EnrollmentForm
from courses.models import Assignment
from attendance.models import Attendance

@login_required(login_url='users:login')
def student_dashboard(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        student = None  # For non-students, show empty dashboard
    assignments = Assignment.objects.filter(course__enrollments__student=student).distinct().order_by('deadline') if student else []
    enrollments = student.enrollments.all() if student else []
    context = {
        'student': student,
        'assignments': assignments,
        'enrollments': enrollments
    }
    return render(request, 'students/dashboard.html', context)

@login_required(login_url='users:login')
def enroll_course(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found. Contact admin.')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, student=student)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            enrollment.save()
            messages.success(request, 'Successfully enrolled in the course.')
            return redirect('students:dashboard')
    else:
        form = EnrollmentForm(student=student)
    
    return render(request, 'students/enroll.html', {'form': form})

@login_required(login_url='users:login')
def mark_attendance(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found. Contact admin.')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment')
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, student=student)
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=timezone.now().date(),
                defaults={'status': 'Present'}
            )
            messages.success(request, 'Attendance marked successfully for today.')
        except Enrollment.DoesNotExist:
            messages.error(request, 'Invalid enrollment selected.')
        return redirect('students:dashboard')
    
    return redirect('students:dashboard')

@login_required(login_url='users:login')
def view_attendance(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, 'Student profile not found. Contact admin.')
        return redirect('students:dashboard')
    
    enrollments = student.enrollments.all()
    attendances = Attendance.objects.filter(enrollment__student=student).select_related('enrollment__course', 'enrollment__faculty').order_by('-date')
    context = {
        'student': student,
        'enrollments': enrollments,
        'attendances': attendances
    }
    return render(request, 'students/view_attendance.html', context)
