import yt_dlp
import os
from pathlib import Path
import threading
from typing import Dict

# Store progress for each task (in-memory, for SSE)
download_progress: Dict[int, int] = {}
_progress_lock = threading.Lock()

def update_progress(task_id: int, percent: int):
    """Thread-safe progress update."""
    with _progress_lock:
        download_progress[task_id] = min(percent, 100)

def get_progress(task_id: int) -> int:
    """Get current progress for a task."""
    with _progress_lock:
        return download_progress.get(task_id, 0)

# Directory for downloaded files
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
        # For audio
        return 'bestaudio/best'
    else:
        # For video
        quality_str = quality_map.get(quality, 'best')
        return f'{quality_str}[ext=mp4]/best[ext=mp4]/best'

def download_media(url: str, format_type: str, quality: str, task_id: int) -> tuple[str, str]:
    """
    Download media from URL and return (file_path, error_message)
    """
    output_template = str(DOWNLOAD_DIR / f"task_{task_id}_%(title)s.%(ext)s")
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                percent = int(d['downloaded_bytes'] / total * 100)
                update_progress(task_id, percent)


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
            'progress_hooks': [progress_hook],
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
            # Get the path to the downloaded file
            if format_type == 'mp3':
                # For mp3 the file will have a .mp3 extension
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                if not os.path.exists(filename):
                    # Try to find the file with a different extension
                    base = os.path.splitext(ydl.prepare_filename(info))[0]
                    filename = base + '.mp3'
            else:
                filename = ydl.prepare_filename(info)
            
            return filename, None
    except Exception as e:
        return None, str(e)