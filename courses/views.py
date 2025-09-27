from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Course
from students.models import Student

def _student_enrolled(student, course):
    """
    Helper: returns True if student is enrolled in course.
    """
    if not student or not student.course:
        return False
    return student.course_id == course.id

def course_list(request):
    courses = Course.objects.all()
    student = None
    suggested_courses = []
    if request.user.is_authenticated and request.user.role == 'student':
        student = Student.objects.filter(user=request.user).first()
        if student and student.course:
            suggested_courses = Course.objects.exclude(id=student.course.id)
        else:
            suggested_courses = courses
    else:
        suggested_courses = courses
    context = {
        'courses': courses,
        'suggested_courses': suggested_courses,
        'student': student,
    }
    return render(request, 'courses/list.html', context)

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    faculty_list = course.faculty.all() if hasattr(course, 'faculty') else []
    student = None
    if request.user.is_authenticated and request.user.role == 'student':
        student = Student.objects.filter(user=request.user).first()
    context = {
        'course': course,
        'faculty_list': faculty_list,
        'student': student,
    }
    return render(request, 'courses/detail.html', context)

@login_required(login_url='users:login')
def enroll_course(request, course_id):
    # Only students can enroll
    if request.user.role != 'student':
        return HttpResponseForbidden("Only students can enroll in courses.")
    course = get_object_or_404(Course, id=course_id)
    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, "Student profile not found. Ask admin to create your student profile.")
        return redirect('courses:list')

    # If POST is used (we handle both GET+POST but prefer POST for enroll)
    if request.method == 'POST' or request.method == 'GET':
        student.course = course
        student.save()
        messages.success(request, f"Enrolled in {course.name}.")
        return redirect('courses:detail', course_id=course.id)
