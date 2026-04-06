from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from functools import wraps
from .forms import RegisterForm, LoginForm
from .models import User


def admin_required(view_func):
    """Decorator: login + admin role tekshirish"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'admin':
            return redirect('student_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# --------------------------
# HOME
# --------------------------
def home_view(request):
    return render(request, 'home.html')


# --------------------------
# REGISTER
# --------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == "admin":
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


# --------------------------
# LOGIN
# --------------------------
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.role == "admin":
                    return redirect('admin_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                form.add_error(None, "Login yoki parol noto'g'ri")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# --------------------------
# LOGOUT (POST only)
# --------------------------
@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')


# --------------------------
# ADMIN DASHBOARD (dynamic stats)
# --------------------------
@admin_required
def admin_dashboard(request):
    from courses.models import Course, Module, Lesson
    context = {
        'user_count': User.objects.count(),
        'course_count': Course.objects.count(),
        'module_count': Module.objects.count(),
        'lesson_count': Lesson.objects.count(),
    }
    return render(request, 'admin_dashboard.html', context)


# --------------------------
# STUDENT DASHBOARD (dynamic stats)
# --------------------------
@login_required
def student_dashboard(request):
    if request.user.role != "student":
        return redirect('admin_dashboard')

    from courses.models import Enrollment, LessonProgress, Lesson

    enrollments = Enrollment.objects.filter(student=request.user)
    active_courses = enrollments.filter(completed=False).count()
    completed_courses = enrollments.filter(completed=True).count()

    total_lessons = Lesson.objects.filter(
        module__course__enrollment__student=request.user
    ).distinct().count()
    completed_lessons = LessonProgress.objects.filter(
        student=request.user, completed=True
    ).count()
    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons else 0

    recent_enrollments = enrollments.select_related('course').order_by('-enrolled_at')[:3]

    context = {
        'active_courses': active_courses,
        'completed_courses': completed_courses,
        'progress_percent': progress_percent,
        'recent_enrollments': recent_enrollments,
    }
    return render(request, 'student_dashboard.html', context)


# --------------------------
# ADMIN: FOYDALANUVCHILARNI BOSHQARISH
# --------------------------
@admin_required
def admin_users_view(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.all()
    return render(request, 'admin_users.html', {'users': users})


@admin_required
@require_POST
def toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_users')


@admin_required
@require_POST
def change_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.role == 'student':
        user.role = 'admin'
    else:
        user.role = 'student'
    user.save()
    return redirect('admin_users')


@admin_required
@require_POST
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_users')