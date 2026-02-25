from django.urls import path
from .views import (admin_edit_lesson, admin_modules, admin_add_module, 
                    admin_lessons, admin_add_lesson,admin_delete_lesson, student_courses,
                     student_lesson_view,student_courses, student_course_detail, student_lesson_view,generate_certificate)
from .views import (
    admin_courses,
    admin_add_course,
    admin_edit_course,
    admin_delete_course
)

urlpatterns = [
    path('', admin_courses, name='admin_courses'),
    path('maneger/courses/add/', admin_add_course, name='admin_add_course'),
    path('maneger/courses/edit/<int:course_id>/', admin_edit_course, name='admin_edit_course'),
    path('maneger/courses/delete/<int:course_id>/', admin_delete_course, name='admin_delete_course'),

     # Modules
    path('<int:course_id>/modules/', admin_modules, name='admin_modules'),
    path('<int:course_id>/modules/add/', admin_add_module, name='admin_add_module'),

    # Lessons
    path('<int:course_id>/modules/<int:module_id>/lessons/', admin_lessons, name='admin_lessons'),
    path('<int:course_id>/modules/<int:module_id>/lessons/add/', admin_add_lesson, name='admin_add_lesson'),
    path('<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/edit/', admin_edit_lesson, name='admin_edit_lesson'),
    path('<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/delete/', admin_delete_lesson, name='admin_delete_lesson'),

    
    path('student/courses/', student_courses, name='student_courses'),
    path('student/courses/<int:course_id>/', student_course_detail, name='student_course_detail'),
    path('student/courses/<int:course_id>/modules/<int:module_id>/lessons/<int:lesson_id>/',student_lesson_view, name='student_lesson_view'),
    path(
    'student/course/<int:course_id>/certificate/',generate_certificate,name='generate_certificate'),
]