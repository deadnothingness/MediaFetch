from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models, schemas
from .services.downloader import download_media
from .services.llm_parser import parse_request
from pathlib import Path

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
    # Create a new db session for background task (avoid shared session issues)
    from .database import SessionLocal
    db = SessionLocal()
    try:
        task = db.query(models.DownloadTask).filter(models.DownloadTask.id == task_id).first()
        if task:
            task.status = models.TaskStatus.DOWNLOADING
            db.commit()

            file_path, error = download_media(url, format_type, quality, task_id)

            if error:
                task.status = models.TaskStatus.FAILED
                task.error_message = error
            else:
                task.status = models.TaskStatus.COMPLETED
                task.file_path = file_path
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
    
    if request.quality not in ['low', 'medium', 'high']:
        raise HTTPException(status_code=400, detail="Quality must be 'low', 'medium', or 'high'")
    
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
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=task.file_path,
        filename=os.path.basename(task.file_path),
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