from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    admin_dashboard,
    student_dashboard,
    home_view,
    admin_users_view,
    toggle_active,
    delete_user,
    change_role,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # DASHBOARD
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),

    # ADMIN: Foydalanuvchilarni boshqarish
    path('manager/users/', admin_users_view, name='admin_users'),
    path('manager/users/toggle/<int:user_id>/', toggle_active, name='toggle_active'),
    path('manager/users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('manager/users/change-role/<int:user_id>/', change_role, name='change_role'),
]