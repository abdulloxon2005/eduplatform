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
    video_thumbnail = models.ImageField(
        upload_to='lesson_thumbnails/', null=True, blank=True,
        help_text="Avtomatik yaratiladi"
    )
    video_duration = models.CharField(
        max_length=20, blank=True, null=True,
        help_text="Video davomiyligi (HH:MM:SS)"
    )
    original_video_size = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Original hajm (bayt)"
    )
    compressed_video_size = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Siqilgan hajm (bayt)"
    )
    is_video_compressed = models.BooleanField(default=False)
    content = models.TextField(blank=True, null=True)
    pdf = models.FileField(upload_to='lesson_pdfs/', null=True, blank=True)
    preview = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    @property
    def original_size_display(self):
        """Original hajmni o'qilishi oson formatda ko'rsatish"""
        if self.original_video_size:
            return self._format_size(self.original_video_size)
        return None

    @property
    def compressed_size_display(self):
        """Siqilgan hajmni o'qilishi oson formatda ko'rsatish"""
        if self.compressed_video_size:
            return self._format_size(self.compressed_video_size)
        return None

    @property
    def compression_ratio(self):
        """Siqish foizini hisoblash"""
        if self.original_video_size and self.compressed_video_size:
            return round(
                (1 - self.compressed_video_size / self.original_video_size) * 100, 1
            )
        return 0

    @staticmethod
    def _format_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

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