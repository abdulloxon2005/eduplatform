"""
Django signals for video auto-compression.
Video yuklanganda avtomatik siqish va thumbnail yaratish.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Lesson
from .video_utils import process_uploaded_video, format_duration

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lesson)
def auto_compress_lesson_video(sender, instance, **kwargs):
    """
    Lesson saqlanganida video avtomatik siqiladi.
    is_video_compressed=False bo'lsa va video mavjud bo'lsa ishlaydi.
    """
    # Agar video yo'q yoki allaqachon siqilgan bo'lsa, o'tkazib yuboramiz
    if not instance.video or instance.is_video_compressed:
        return

    # Kompressiya sozlamalari
    compression_settings = getattr(settings, 'VIDEO_COMPRESSION', {})

    # Agar kompressiya o'chirilgan bo'lsa
    if not compression_settings.get('ENABLED', True):
        return

    logger.info(f"Video kompressiya boshlandi: {instance.title}")

    try:
        result = process_uploaded_video(
            video_field_path=instance.video.name,
            media_root=settings.MEDIA_ROOT,
            compression_settings=compression_settings,
        )

        if result:
            update_fields = {
                'original_video_size': result['original_size'],
                'compressed_video_size': result['compressed_size'],
                'is_video_compressed': True,
            }

            # Duration
            if result.get('duration'):
                update_fields['video_duration'] = format_duration(result['duration'])

            # Agar video nomi o'zgargan bo'lsa (yangi .mp4 fayl)
            if result.get('new_video_name'):
                update_fields['video'] = result['new_video_name']

            # Thumbnail
            if result.get('thumbnail_name'):
                update_fields['video_thumbnail'] = result['thumbnail_name']

            # Signal qayta chaqirilmasligi uchun .update() ishlatamiz
            Lesson.objects.filter(id=instance.id).update(**update_fields)

            ratio = result.get('compression_ratio', 0)
            logger.info(
                f"Video kompressiya tugadi: {instance.title} | "
                f"Kamaytirish: {ratio}%"
            )
        else:
            # FFmpeg mavjud emas yoki xato — faqat flagni o'rnatamiz
            Lesson.objects.filter(id=instance.id).update(is_video_compressed=True)
            logger.warning(f"Video kompressiya o'tkazib yuborildi: {instance.title}")

    except Exception as e:
        logger.error(f"Video kompressiya xatosi: {e}")
        # Xato bo'lsa ham flagni o'rnatamiz (qayta urinmaslik uchun)
        Lesson.objects.filter(id=instance.id).update(is_video_compressed=True)
