from django.urls import path
from .views import (
    admin_courses,
    admin_add_course,
    admin_edit_course,
    admin_delete_course,
    admin_modules,
    admin_add_module,
    admin_lessons,
    admin_add_lesson,
    admin_edit_lesson,
    admin_delete_lesson,
    student_courses,
    student_course_detail,
    student_lesson_view,
    student_course_completed,
    generate_certificate,
)

urlpatterns = [
    # Admin: Courses
    path('admin/', admin_courses, name='admin_courses'),
    path('admin/add/', admin_add_course, name='admin_add_course'),
    path('admin/edit/<int:course_id>/', admin_edit_course, name='admin_edit_course'),
    path('admin/delete/<int:course_id>/', admin_delete_course, name='admin_delete_course'),

    # Admin: Modules
    path('admin/<int:course_id>/modules/', admin_modules, name='admin_modules'),
    path('admin/<int:course_id>/modules/add/', admin_add_module, name='admin_add_module'),

    # Admin: Lessons
    path('admin/<int:course_id>/modules/<int:module_id>/lessons/', admin_lessons, name='admin_lessons'),
    path('admin/<int:course_id>/modules/<int:module_id>/lessons/add/', admin_add_lesson, name='admin_add_lesson'),
    path('admin/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/edit/', admin_edit_lesson, name='admin_edit_lesson'),
    path('admin/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/delete/', admin_delete_lesson, name='admin_delete_lesson'),

    # Student
    path('', student_courses, name='student_courses'),
    path('<int:course_id>/', student_course_detail, name='student_course_detail'),
    path('<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/', student_lesson_view, name='student_lesson_view'),
    path('<int:course_id>/completed/', student_course_completed, name='student_course_completed'),
    path('<int:course_id>/certificate/', generate_certificate, name='generate_certificate'),
]