from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import User


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
            user = form.save()  # role = "student" avtomatik
            login(request, user)  # registerdan so'ng login qilinadi

            # Role bo‘yicha yo‘naltirish
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

                # Role bo‘yicha yo‘naltirish
                if user.role == "admin":
                    return redirect('admin_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                # Error message
                form.add_error(None, "Login yoki parol noto‘g‘ri")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


# --------------------------
# LOGOUT
# --------------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# --------------------------
# ADMIN DASHBOARD
# --------------------------
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect('student_dashboard')

    return render(request, 'admin_dashboard.html')


# --------------------------
# STUDENT DASHBOARD
# --------------------------
@login_required
def student_dashboard(request):
    if request.user.role != "student":
        return redirect('admin_dashboard')

    return render(request, 'student_dashboard.html')


# --------------------------
# ADMIN: FOYDALANUVCHILARNI BOSHQARISH
# --------------------------
@login_required
def admin_users_view(request):
    if request.user.role != "admin":
        return redirect('student_dashboard')

    query = request.GET.get('q')
    if query:
        users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.all()

    return render(request, 'admin_users.html', {'users': users})


@login_required
def toggle_active(request, user_id):
    if request.user.role != 'admin':
        return redirect('student_dashboard')

    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_users')

def change_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.role == 'student':
        user.role = 'admin'  # Modeldagi role maydoniga qarab o'zgartiring
    else:
        user.role = 'student'
    user.save()
    return redirect('admin_users')


@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('student_dashboard')

    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_users')