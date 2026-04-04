import yt_dlp
import os
import uuid
from pathlib import Path

# Папка для сохранения файлов
DOWNLOAD_DIR = Path(__file__).parent.parent.parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

def get_quality_format(quality: str, format_type: str):
    """Convert quality and format to yt-dlp format string"""
    quality_map = {
        'low': 'worst',
        'medium': 'best',
        'high': 'best'
    }
    
    if format_type == 'mp3':
        # Для аудио
        return 'bestaudio/best'
    else:
        # Для видео
        quality_str = quality_map.get(quality, 'best')
        return f'{quality_str}[ext=mp4]/best[ext=mp4]/best'

def download_media(url: str, format_type: str, quality: str, task_id: int) -> tuple[str, str]:
    """
    Download media from URL and return (file_path, error_message)
    """
    output_template = str(DOWNLOAD_DIR / f"task_{task_id}_%(title)s.%(ext)s")
    
    if format_type == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
    else:
        format_str = get_quality_format(quality, format_type)
        ydl_opts = {
            'format': format_str,
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Получаем путь к скачанному файлу
            if format_type == 'mp3':
                # Для mp3 файл будет иметь расширение .mp3
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                if not os.path.exists(filename):
                    # Пробуем найти файл с другим расширением
                    base = os.path.splitext(ydl.prepare_filename(info))[0]
                    filename = base + '.mp3'
            else:
                filename = ydl.prepare_filename(info)
            
            return filename, None
    except Exception as e:
        return None, str(e)