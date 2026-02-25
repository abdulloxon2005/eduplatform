from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Module, Lesson, Enrollment,LessonProgress
from .forms import CourseForm, ModuleForm, LessonForm
from django.http import JsonResponse
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
import io
from datetime import date

@login_required
def admin_courses(request):
    if request.user.role != 'admin':
        return redirect('student_dashboard')

    courses = Course.objects.all()
    return render(request, 'admin_courses.html', {'courses': courses})


@login_required
def admin_add_course(request):
    if request.user.role != 'admin':
        return redirect('student_dashboard')

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_courses')
    else:
        form = CourseForm()

    return render(request, 'admin_add_course.html', {'form': form})


@login_required
def admin_edit_course(request, course_id):
    if request.user.role != 'admin':
        return redirect('student_dashboard')

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('admin_courses')
    else:
        form = CourseForm(instance=course)

    return render(request, 'admin_add_course.html', {'form': form})


@login_required
def admin_delete_course(request, course_id):
    if request.user.role != 'admin':
        return redirect('student_dashboard')

    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('admin_courses')

# --------------------------
# Module Views
# --------------------------
@login_required
def admin_modules(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = Module.objects.filter(course=course).order_by('order')
    return render(request, 'admin_modules.html', {'course': course, 'modules': modules})

@login_required
def admin_add_module(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            return redirect('admin_modules', course_id=course.id)
    else:
        form = ModuleForm()
    return render(request, 'admin_add_module.html', {'form': form, 'course': course})

# --------------------------
# Lesson Views
# --------------------------
@login_required
def admin_lessons(request, course_id, module_id):
    module = get_object_or_404(Module, id=module_id, course_id=course_id)
    lessons = Lesson.objects.filter(module=module).order_by('order')

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            return redirect('admin_lessons', course_id=course_id, module_id=module_id)
    else:
        form = LessonForm()

    return render(request, 'admin_lessons.html', {
        'module': module,
        'lessons': lessons,
        'form': form,
        'course_id': course_id
    })


@login_required
def admin_add_lesson(request, course_id, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            return redirect('admin_lessons', course_id=course_id, module_id=module.id)
    else:
        form = LessonForm()
    return render(request, 'admin_add_lesson.html', {'form': form, 'module': module})

@login_required
def admin_edit_lesson(request, course_id, module_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module_id=module_id)
    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('admin_lessons', course_id=course_id, module_id=module_id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'admin_edit_lesson.html', {
        'form': form,
        'module_id': module_id,
        'course_id': course_id,
        'lesson': lesson,
    })


@login_required
def admin_delete_lesson(request, course_id, module_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, module_id=module_id)
    lesson.delete()
    return redirect('admin_lessons', course_id=course_id, module_id=module_id)


@login_required
def student_courses(request):
    courses = Course.objects.all()
    return render(request, 'student_courses.html', {'courses': courses})


@login_required
def student_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = Module.objects.filter(course=course).order_by('order')

    # Enrollment avtomatik yaratish (hamma bepul kurslar uchun)
    enrollment, created = Enrollment.objects.get_or_create(
        course=course,
        student=request.user
    )

    return render(request, 'student_course_detail.html', {
        'course': course,
        'modules': modules,
        'enrolled': True  # endi har doim True
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Module, Lesson, Enrollment, LessonProgress


@login_required
def student_lesson_view(request, course_id, module_id, lesson_id):

    course = get_object_or_404(Course, id=course_id)
    module = get_object_or_404(Module, id=module_id, course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id, module=module)

    # 🔹 Enrollment tekshirish
    enrolled = Enrollment.objects.filter(
        course=course,
        student=request.user
    ).exists()

    # 🔒 Agar preview bo‘lmasa va student yozilmagan bo‘lsa
    if not lesson.preview and not enrolled:
        return render(request, 'lesson_locked.html', {'lesson': lesson})

    # ===================================================
    # 🔒 OLDINGI DARSNI TEKSHIRISH (SHU YERGA QO‘SHILDI)
    # ===================================================
    previous_lesson = Lesson.objects.filter(
        module=module,
        order__lt=lesson.order
    ).order_by('-order').first()

    if previous_lesson:
        prev_completed = LessonProgress.objects.filter(
            student=request.user,
            lesson=previous_lesson,
            completed=True
        ).exists()

        if not prev_completed:
            return render(request, 'lesson_locked.html', {
                'lesson': lesson,
                'reason': "Avval oldingi darsni tugating."
            })

    # 🔹 Progress obyekt
    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    # =========================
    # POST — darsni tugatish
    # =========================
    if request.method == "POST":

        if not progress.completed:
            progress.completed = True
            progress.save()

        # 🔹 1. Shu moduldagi keyingi dars
        next_lesson = Lesson.objects.filter(
            module=module,
            order__gt=lesson.order
        ).order_by('order').first()

        if next_lesson:
            return redirect(
                'student_lesson_view',
                course_id=course.id,
                module_id=module.id,
                lesson_id=next_lesson.id
            )

        # 🔹 2. Keyingi modul
        next_module = Module.objects.filter(
            course=course,
            order__gt=module.order
        ).order_by('order').first()

        if next_module:
            first_lesson = Lesson.objects.filter(
                module=next_module
            ).order_by('order').first()

            if first_lesson:
                return redirect(
                    'student_lesson_view',
                    course_id=course.id,
                    module_id=next_module.id,
                    lesson_id=first_lesson.id
                )

        # 🔹 3. Kurs tugagan
        return redirect('student_course_completed', course_id=course.id)
        # 🔒 Agar bu modulning birinchi darsi bo‘lsa,
# oldingi modul to‘liq tugaganmi tekshiramiz

    if lesson.order == 1:

        previous_module = Module.objects.filter(
            course=course,
            order__lt=module.order
        ).order_by('-order').first()

        if previous_module:

            total_prev_lessons = Lesson.objects.filter(
                module=previous_module
            ).count()

            completed_prev_lessons = LessonProgress.objects.filter(
                student=request.user,
                lesson__module=previous_module,
                completed=True
            ).count()

            if total_prev_lessons != completed_prev_lessons:
                return render(request, 'lesson_locked.html', {
                    'lesson': lesson,
                    'reason': "Avval oldingi modulni to‘liq tugating."
                })

    # =========================
    # PROGRESS HISOBLASH
    # =========================
    total_lessons = Lesson.objects.filter(
        module__course=course
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        lesson__module__course=course,
        completed=True
    ).count()

    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons else 0

    

    # =========================
    # MODUL PROGRESS (SHU YERGA QO‘YILADI)
    # =========================
    total_module_lessons = Lesson.objects.filter(
        module=module
    ).count()

    completed_module_lessons = LessonProgress.objects.filter(
        student=request.user,
        lesson__module=module,
        completed=True
    ).count()

    module_progress_percent = int(
        (completed_module_lessons / total_module_lessons) * 100
    ) if total_module_lessons else 0

    # Moduldagi barcha darslar
    module_lessons = Lesson.objects.filter(
        module=module
    ).order_by('order')

    # Tugatilgan darslar ID ro‘yxati
    completed_ids = LessonProgress.objects.filter(
        student=request.user,
        lesson__module=module,
        completed=True
    ).values_list('lesson_id', flat=True)

    return render(request, 'student_lesson.html', {
    'lesson': lesson,
    'progress_percent': progress_percent,
    'module_progress_percent': module_progress_percent,
    'is_completed': progress.completed,
    'module_lessons': module_lessons,
    'completed_ids': completed_ids
})

    


@login_required
def generate_certificate(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    total_lessons = Lesson.objects.filter(
        module__course=course
    ).count()

    completed_lessons = LessonProgress.objects.filter(
        student=request.user,
        lesson__module__course=course,
        completed=True
    ).count()

    # ❌ Agar kurs tugamagan bo‘lsa
    if total_lessons != completed_lessons:
        return HttpResponse("Kurs hali to‘liq tugatilmagan.")

    # ✅ PDF yaratish
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>SERTIFIKAT</b>", styles['Title']))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(
        Paragraph(
            f"{request.user.username} muvaffaqiyatli tarzda "
            f"{course.title} kursini tugatdi.",
            styles['Normal']
        )
    )

    elements.append(Spacer(1, 0.5 * inch))

    elements.append(
        Paragraph(
            f"Sana: {date.today()}",
            styles['Normal']
        )
    )

    doc.build(elements)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{course.id}.pdf"'

    return response