from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models, schemas
from .services.downloader import download_media, get_progress, update_progress
from .services.llm_parser import parse_request
from pathlib import Path

import asyncio
import json
import os

# Path to frontend folder – read from env or use default
FRONTEND_PATH = os.getenv("FRONTEND_PATH", str(Path(__file__).parent.parent.parent / "frontend"))

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MediaFetch API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_frontend():
    """Serve the main HTML page"""
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

@app.get("/style.css")
async def serve_css():
    """Serve CSS file"""
    return FileResponse(os.path.join(FRONTEND_PATH, "style.css"), media_type="text/css")

@app.get("/app.js")
async def serve_js():
    """Serve JavaScript file"""
    return FileResponse(os.path.join(FRONTEND_PATH, "app.js"), media_type="application/javascript")

def process_download(task_id: int, url: str, format_type: str, quality: str):
    """Background task to process download"""
    from .database import SessionLocal
    db = SessionLocal()
    try:
        task = db.query(models.DownloadTask).filter(models.DownloadTask.id == task_id).first()
        if task:
            task.status = models.TaskStatus.DOWNLOADING
            db.commit()

            file_path, display_name, error = download_media(url, format_type, quality, task_id)

            if error:
                task.status = models.TaskStatus.FAILED
                task.error_message = error
            else:
                task.status = models.TaskStatus.COMPLETED
                task.file_path = file_path
                task.display_name = display_name
                update_progress(task_id, 100)
            db.commit()
    finally:
        db.close()

@app.post("/download", response_model=schemas.DownloadResponse)
async def create_download(
    request: schemas.DownloadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if request.format not in ['mp3', 'mp4']:
        raise HTTPException(status_code=400, detail="Format must be 'mp3' or 'mp4'")
    
    allowed_qualities = ['360p', '720p', '1080p', 'best', '128k', '192k', '320k']
    if request.quality not in allowed_qualities:
        raise HTTPException(status_code=400, detail=f"Quality must be one of: {', '.join(allowed_qualities)}")
    
    task = models.DownloadTask(
        url=request.url,
        format=request.format,
        quality=request.quality,
        status=models.TaskStatus.PENDING
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    background_tasks.add_task(
        process_download,
        task.id,
        request.url,
        request.format,
        request.quality
    )
    
    return schemas.DownloadResponse(
        task_id=task.id,
        status=task.status.value,
        message="Download started"
    )

@app.get("/tasks", response_model=list[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.DownloadTask).order_by(models.DownloadTask.created_at.desc()).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.DownloadTask).filter(models.DownloadTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/download/{task_id}")
def download_file(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.DownloadTask).filter(models.DownloadTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != models.TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="File not ready yet")
    
    if not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail=f"File not found on server: {task.file_path}")
    
    # Use display_name for download filename if available
    if task.display_name:
        download_filename = f"{task.display_name}.{task.format}"
    else:
        download_filename = os.path.basename(task.file_path)
    
    return FileResponse(
        path=task.file_path,
        filename=download_filename,
        media_type="application/octet-stream"
    )

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/llm/parse", response_model=schemas.LLMParseResponse)
async def parse_llm_request(request: schemas.LLMParseRequest):
    """
    Parse natural language request using LLM.
    Extracts URL, format, quality, or search query.
    """
    result = await parse_request(request.message)
    
    return schemas.LLMParseResponse(
        url=result.get("url"),
        format=result.get("format"),
        quality=result.get("quality", "medium"),
        search_query=result.get("search_query"),
        original_message=request.message
    )

@app.get("/tasks/{task_id}/progress")
async def stream_progress(task_id: int, db: Session = Depends(get_db)):
    """Stream download progress via Server-Sent Events."""
    # First check if task exists
    task = db.query(models.DownloadTask).filter(models.DownloadTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    async def event_generator():
        while True:
            progress = get_progress(task_id)
            # Also check if task is completed or failed
            task_status = db.query(models.DownloadTask).filter(models.DownloadTask.id == task_id).first()
            if task_status:
                if task_status.status == models.TaskStatus.COMPLETED:
                    yield f"data: {json.dumps({'progress': 100, 'status': 'completed'})}\n\n"
                    break
                elif task_status.status == models.TaskStatus.FAILED:
                    yield f"data: {json.dumps({'progress': progress, 'status': 'failed', 'error': task_status.error_message})}\n\n"
                    break
            
            yield f"data: {json.dumps({'progress': progress, 'status': 'downloading'})}\n\n"
            
            if progress >= 100:
                break
            await asyncio.sleep(0.5)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")