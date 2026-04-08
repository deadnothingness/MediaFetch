from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"

class DownloadTask(Base):
    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    format = Column(String, nullable=False)  # 'mp3' or 'mp4'
    quality = Column(String, nullable=False)  # '360p', '720p', '1080p', 'best' for video; '128k', '192k', '320k' for audio
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    progress = Column(Integer, default=0)  # 0-100 percentage