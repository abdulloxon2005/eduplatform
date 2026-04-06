from django import forms
from .models import Course, Module, Lesson

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg', 'video/avi']
ALLOWED_PDF_TYPES = ['application/pdf']
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def validate_file_type(file, allowed_types, label="Fayl"):
    """Fayl turini tekshirish"""
    if file and hasattr(file, 'content_type'):
        if file.content_type not in allowed_types:
            raise forms.ValidationError(
                f"{label} turi noto'g'ri. Ruxsat etilgan: {', '.join(allowed_types)}"
            )
        if file.size > MAX_FILE_SIZE:
            raise forms.ValidationError(
                f"{label} hajmi juda katta. Maksimal: {MAX_FILE_SIZE // (1024*1024)} MB"
            )


# --------------------------
# COURSE FORM
# --------------------------
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title',
            'description',
            'price',
            'discount',
            'category',
            'duration',
            'cover_image',
            'promo_video',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'promo_video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_cover_image(self):
        file = self.cleaned_data.get('cover_image')
        validate_file_type(file, ALLOWED_IMAGE_TYPES, "Rasm")
        return file

    def clean_promo_video(self):
        file = self.cleaned_data.get('promo_video')
        validate_file_type(file, ALLOWED_VIDEO_TYPES, "Video")
        return file

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount and (discount < 0 or discount > 100):
            raise forms.ValidationError("Chegirma 0 dan 100 gacha bo'lishi kerak.")
        return discount


# --------------------------
# ModuleForm
# --------------------------
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# --------------------------
# LessonForm
# --------------------------
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video', 'pdf', 'content', 'preview', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_video(self):
        file = self.cleaned_data.get('video')
        validate_file_type(file, ALLOWED_VIDEO_TYPES, "Video")
        return file

    def clean_pdf(self):
        file = self.cleaned_data.get('pdf')
        validate_file_type(file, ALLOWED_PDF_TYPES, "PDF")
        return file