"""
Video compression va processing utilities.
FFmpeg yordamida videolarni siqish, thumbnail yaratish va metadata olish.
"""

import subprocess
import os
import json
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def is_ffmpeg_available():
    """FFmpeg o'rnatilganligini tekshirish"""
    return shutil.which('ffmpeg') is not None


def get_video_info(file_path):
    """
    FFprobe yordamida video metadata olish.
    Returns: dict with duration, size, width, height or None
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data.get('format', {}).get('duration', 0))
            size = int(data.get('format', {}).get('size', 0))

            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break

            width = int(video_stream.get('width', 0)) if video_stream else 0
            height = int(video_stream.get('height', 0)) if video_stream else 0

            return {
                'duration': duration,
                'size': size,
                'width': width,
                'height': height,
            }
    except Exception as e:
        logger.error(f"FFprobe xatosi: {e}")
    return None


def format_duration(seconds):
    """Sekundlarni HH:MM:SS formatga o'tkazish"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_file_size(size_bytes):
    """Baytlarni o'qilishi oson formatga o'tkazish"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def compress_video(input_path, output_path, max_height=720, crf=28,
                   preset='medium', audio_bitrate='128k'):
    """
    FFmpeg yordamida videoni siqish.

    Args:
        input_path: Kirish video yo'li
        output_path: Chiqish video yo'li
        max_height: Maksimal balandlik (720 = 720p)
        crf: Sifat koeffitsienti (18-32, past = sifatli, katta fayl)
        preset: Kodlash tezligi (ultrafast, fast, medium, slow)
        audio_bitrate: Audio bitrate

    Returns:
        True agar muvaffaqiyatli, False aks holda
    """
    try:
        # Faqat kichiklashtirish, kattalashtirmaslik
        scale_filter = f"scale=-2:'min({max_height},ih)'"

        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vcodec', 'libx264',
            '-crf', str(crf),
            '-preset', preset,
            '-vf', scale_filter,
            '-acodec', 'aac',
            '-b:a', audio_bitrate,
            '-movflags', '+faststart',  # Web streaming uchun tez start
            '-y',  # Mavjud faylni qayta yozish
            str(output_path)
        ]

        logger.info(f"Video siqish boshlandi: {input_path}")
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=1800  # 30 daqiqa timeout
        )

        if result.returncode == 0:
            logger.info(f"Video siqish tugadi: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg xatosi: {result.stderr[:500]}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("FFmpeg vaqt tugadi (timeout)")
        return False
    except Exception as e:
        logger.error(f"Video siqish xatosi: {e}")
        return False


def generate_thumbnail(video_path, output_path, time='00:00:01'):
    """
    Videodan thumbnail (eskiz rasm) yaratish.

    Args:
        video_path: Video fayl yo'li
        output_path: Thumbnail saqlanadigan joy
        time: Qaysi sekunddan olish (default: 1-sekund)

    Returns:
        True agar muvaffaqiyatli
    """
    try:
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-ss', time,
            '-vframes', '1',
            '-vf', 'scale=640:-2',
            '-q:v', '2',
            '-y',
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Thumbnail yaratish xatosi: {e}")
        return False


def process_uploaded_video(video_field_path, media_root, compression_settings=None):
    """
    Video yuklangandan keyin to'liq qayta ishlash:
    1. Original ma'lumotlarni olish
    2. Kompressiya qilish
    3. Thumbnail yaratish

    Args:
        video_field_path: Video faylning MEDIA_ROOT ga nisbatan yo'li
        media_root: MEDIA_ROOT yo'li
        compression_settings: Siqish sozlamalari dict

    Returns:
        dict with results or None if failed
    """
    if not is_ffmpeg_available():
        logger.warning("FFmpeg mavjud emas. Kompressiya o'tkazib yuborildi.")
        return None

    settings = compression_settings or {}
    max_height = settings.get('MAX_HEIGHT', 720)
    crf = settings.get('CRF', 28)
    preset = settings.get('PRESET', 'medium')
    audio_bitrate = settings.get('AUDIO_BITRATE', '128k')

    original_path = os.path.join(media_root, video_field_path)

    if not os.path.exists(original_path):
        logger.error(f"Video fayl topilmadi: {original_path}")
        return None

    # Original ma'lumotlar
    original_size = os.path.getsize(original_path)
    info = get_video_info(original_path)

    # Siqilgan fayl yo'li
    base, ext = os.path.splitext(original_path)
    compressed_path = f"{base}_compressed.mp4"

    # Kompressiya
    success = compress_video(
        original_path, compressed_path,
        max_height=max_height, crf=crf,
        preset=preset, audio_bitrate=audio_bitrate
    )

    result = {
        'original_size': original_size,
        'compressed_size': original_size,
        'duration': info.get('duration') if info else None,
        'compression_ratio': 0,
        'new_video_name': None,
        'thumbnail_name': None,
    }

    if success and os.path.exists(compressed_path):
        compressed_size = os.path.getsize(compressed_path)

        # Faqat kichikroq bo'lsa almashtiramiz
        if compressed_size < original_size:
            os.remove(original_path)
            new_path = f"{base}.mp4"
            os.rename(compressed_path, new_path)

            relative_path = os.path.relpath(new_path, media_root)
            result['new_video_name'] = relative_path.replace('\\', '/')
            result['compressed_size'] = compressed_size
            result['compression_ratio'] = round(
                (1 - compressed_size / original_size) * 100, 1
            )

            logger.info(
                f"Video siqildi: {format_file_size(original_size)} → "
                f"{format_file_size(compressed_size)} "
                f"({result['compression_ratio']}% kamaytirish)"
            )
        else:
            # Siqilgan kattaroq — originalni saqlaymiz
            os.remove(compressed_path)
            logger.info("Siqilgan fayl kattaroq, original saqlanadi.")

    # Thumbnail yaratish
    video_path = result.get('new_video_name')
    if video_path:
        actual_video_path = os.path.join(media_root, video_path)
    else:
        actual_video_path = original_path

    if os.path.exists(actual_video_path):
        thumb_dir = os.path.join(media_root, 'lesson_thumbnails')
        os.makedirs(thumb_dir, exist_ok=True)

        # Unikal thumbnail nomi
        video_basename = os.path.splitext(os.path.basename(actual_video_path))[0]
        thumb_filename = f"thumb_{video_basename}.jpg"
        thumb_path = os.path.join(thumb_dir, thumb_filename)

        if generate_thumbnail(actual_video_path, thumb_path):
            result['thumbnail_name'] = f"lesson_thumbnails/{thumb_filename}"

    return result
