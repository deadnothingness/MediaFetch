import yt_dlp
import os
import re
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

def get_resolution_format(resolution: str, format_type: str = None) -> str:
    """Convert resolution to yt-dlp format string.
    
    Args:
        resolution: Quality setting (e.g., '720p', '1080p', 'best')
        format_type: Ignored, kept for compatibility
    
    Returns:
        yt-dlp format string
    """
    mapping = {
        '360p': 'best[height<=360]',
        '720p': 'best[height<=720]',
        '1080p': 'best[height<=1080]',
        'best': 'best',
    }
    return mapping.get(resolution, 'best')

def generate_display_name(info: dict, format_type: str) -> str:
    """
    Generate a readable filename from video metadata.
    For audio: Artist-Title.mp3
    For video: Title.mp4
    """
    title = info.get('title', 'unknown')
    
    # Remove invalid filename characters and replace spaces with underscores
    def clean_filename(s: str) -> str:
        s = s.replace(' ', '_')
        return re.sub(r'[<>:"/\\|?*]', '', s).strip()
    
    return clean_filename(title)
    
def download_media(url: str, format_type: str, quality: str, task_id: int) -> tuple[str, str, str]:
    """
    Download media from URL and return (file_path, display_name, error_message)
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
        format_str = get_resolution_format(quality)
        ydl_opts = {
            'format': format_str,
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Generate display name from metadata
            display_name = generate_display_name(info, format_type)
            
            # Get the actual downloaded file path
            if format_type == 'mp3':
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                if not os.path.exists(filename):
                    base = os.path.splitext(ydl.prepare_filename(info))[0]
                    filename = base + '.mp3'
            else:
                filename = ydl.prepare_filename(info)
            
            # Rename to pretty name
            pretty_path = DOWNLOAD_DIR / f"{display_name}.{format_type}"
            if os.path.exists(filename) and filename != str(pretty_path):
                os.rename(filename, pretty_path)
                filename = str(pretty_path)
            
            return filename, display_name, None
    except Exception as e:
        return None, None, str(e)