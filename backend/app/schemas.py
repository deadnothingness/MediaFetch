from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .models import TaskStatus

class DownloadRequest(BaseModel):
    url: str
    format: str  # 'mp3' or 'mp4'
    quality: str  # 'low', 'medium', 'high'

class DownloadResponse(BaseModel):
    task_id: int
    status: str
    message: str

class TaskResponse(BaseModel):
    id: int
    url: str
    format: str
    quality: str
    status: TaskStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class LLMParseRequest(BaseModel):
    """Request model for LLM parsing endpoint"""
    message: str

class LLMParseResponse(BaseModel):
    """Response model for LLM parsing endpoint"""
    url: Optional[str] = None
    format: Optional[str] = None
    quality: str = "medium"
    search_query: Optional[str] = None
    original_message: str