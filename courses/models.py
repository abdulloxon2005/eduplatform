from django.db import models
from accounts.models import User
from django.utils import timezone
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.PositiveIntegerField(default=0)  # %
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    duration = models.CharField(max_length=50, help_text="Masalan: 3 oy, 40 soat")
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    promo_video = models.FileField(upload_to='course_videos/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='lesson_videos/', null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    pdf = models.FileField(upload_to='lesson_pdfs/', null=True, blank=True)
    preview = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.module.title} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)  # Kurs tugaganini belgilash

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    class Meta:
        unique_together = ('student', 'course')


class LessonProgress(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"