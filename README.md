# MediaFetch

> A web service for downloading audio (MP3) and video (MP4) from **YouTube** and **VK** by URL, with an integrated **AI chat assistant** that understands natural language requests.

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Quick Start](#quick-start)
4. [Setup Instructions](#setup-instructions)
   - [Local Development](#local-development)
   - [Production Deployment on a VM](#production-deployment-on-a-vm)
5. [Configuration](#configuration)
6. [API Endpoints](#api-endpoints)
7. [Using the Web Interface](#using-the-web-interface)
8. [Known Limitations (v1)](#known-limitations-v1)
9. [Planned for v2](#planned-for-v2)
10. [Troubleshooting](#troubleshooting)
11. [Project Structure](#project-structure)
12. [Testing](#testing)
13. [License](#license)

---

## Overview

MediaFetch is a full-stack web application that lets users download media from YouTube and VK in their preferred format (MP3 or MP4) and quality (low, medium, or high). It features:

- **Manual download form** — paste a URL, choose format and quality, and start downloading.
- **AI chat assistant** — type a natural language request like *"download this video as MP4: <URL>"* and the assistant fills in the form for you.
- **Task-based download system** — every download is tracked as a task with real-time status updates (pending → downloading → completed/failed).
- **File management** — completed files are served directly from the backend via a download link.

The application is built with FastAPI on the backend and vanilla HTML/CSS/JS on the frontend, making it lightweight and easy to deploy.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend framework** | [FastAPI](https://fastapi.tiangolo.com/) 0.115 |
| **Database** | PostgreSQL (via Docker Compose) or SQLite |
| **ORM** | SQLAlchemy 2.0 |
| **Data validation** | Pydantic 2.x |
| **Media downloader** | [yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| **Audio/video conversion** | [ffmpeg](https://ffmpeg.org/) |
| **LLM integration** | Qwen API (Ollama-compatible endpoint) with regex fallback |
| **HTTP client** | httpx |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (ES6+) |
| **ASGI server** | Uvicorn |
| **Containerization** | Docker Compose (PostgreSQL only) |

---

## Quick Start

### Option A — Docker (recommended)

```bash
# 1. Configure environment
cp .env.example .env

# 2. Start everything (PostgreSQL + backend)
cd backend
docker-compose up --build

# 3. Open the web interface
#    http://localhost:8000
```

### Option B — Local development

```bash
# 1. Start PostgreSQL
cd backend && docker-compose up -d postgres

# 2. Install Python dependencies
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env   # edit as needed

# 4. Install ffmpeg (Ubuntu/Debian)
sudo apt install -y ffmpeg

# 5. Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Open the web interface
#    http://localhost:8000
```

---

## Setup Instructions

### Local Development

#### Prerequisites

- **Python 3.10+**
- **Docker & Docker Compose** (for PostgreSQL)
- **ffmpeg** (`sudo apt install ffmpeg` on Ubuntu)
- **Git**

#### Step-by-Step

**1. Clone the repository**

```bash
git clone <repository-url>
cd MediaFetch
```

**2. Start the database**

```bash
cd backend
docker-compose up -d postgres
```

This launches a PostgreSQL 16 container with:
- User: `mediafetch`
- Password: `mediafetch123`
- Database: `mediafetch_db`
- Data persisted in a named volume `postgres_data`.

**3. Set up the Python environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://mediafetch:mediafetch123@localhost:5432/mediafetch_db
LLM_API_URL=http://localhost:11434/api/generate
LLM_MODEL=qwen2:0.5b
# QWEN_API_KEY=your-api-key-here   # Optional — leave empty to use regex fallback
```

**5. Run the server**

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**6. Open the application**

Navigate to `http://localhost:8000` in your browser.

---

### Production Deployment on a VM

#### Prerequisites

- Ubuntu 22.04+ VM with SSH access.
- Docker & Docker Compose installed.
- A domain name (optional, for reverse proxy setup).
- ffmpeg installed on the VM.

#### Step-by-Step

**1. Install system dependencies**

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv ffmpeg git docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in for the docker group to take effect.
```

**2. Clone and configure**

```bash
git clone <repository-url> ~/mediafetch
cd ~/mediafetch
cp .env.example .env
```

Edit `.env` with the production database URL:

```env
DATABASE_URL=postgresql://mediafetch:mediafetch123@localhost:5432/mediafetch_db
```

**3. Start the database**

```bash
cd backend
docker-compose up -d postgres
```

**4. Install Python dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**5. Run with Gunicorn + Uvicorn workers (production)**

```bash
pip install gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**6. (Optional) Set up a systemd service**

Create `/etc/systemd/system/mediafetch.service`:

```ini
[Unit]
Description=MediaFetch Backend
After=network.target docker.service

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/mediafetch/backend
Environment="PATH=/home/ubuntu/mediafetch/backend/venv/bin"
ExecStart=/home/ubuntu/mediafetch/backend/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mediafetch
sudo systemctl start mediafetch
sudo systemctl status mediafetch
```

**7. (Optional) Configure Nginx as a reverse proxy**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Configuration

All configuration is managed through environment variables or a `.env` file placed in the `backend/` directory.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | `postgresql://mediafetch:mediafetch123@localhost:5432/mediafetch_db` | SQLAlchemy database connection string. Supports PostgreSQL and SQLite (`sqlite:///./mediafetch.db`). |
| `LLM_API_URL` | No | `http://localhost:11434/api/generate` | URL of the LLM API endpoint (Ollama-compatible). |
| `LLM_MODEL` | No | `qwen2:0.5b` | Model name to use for LLM parsing. |
| `QWEN_API_KEY` | No | _(empty)_ | API key for the LLM service. **If empty, the LLM tier is skipped and the regex fallback is used automatically.** |

> **Note:** The `llm_parser.py` module reads `LLM_API_URL` and `LLM_MODEL` directly from environment variables via `os.getenv()`, with its own hardcoded defaults (`http://localhost:42005/v1/chat/completions`, model `coder-model`). To override these, set the environment variables explicitly in your `.env` file.

### `.env.example`

```env
DATABASE_URL=postgresql://mediafetch:mediafetch123@localhost:5432/mediafetch_db
LLM_API_URL=http://localhost:11434/api/generate
LLM_MODEL=qwen2:0.5b
# QWEN_API_KEY=your-api-key-here
```

---

## API Endpoints

All endpoints are served from the backend at `http://<server-host>:8000`.

### Health Check

```
GET /api/health
```

**Response (200):**
```json
{ "status": "ok" }
```

---

### Create Download Task

```
POST /download
```

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4",
  "quality": "medium"
}
```

**Response (200):**
```json
{
  "task_id": 1,
  "status": "pending",
  "message": "Download task created"
}
```

**Validation rules:**
- `format` must be `"mp3"` or `"mp4"`.
- `quality` must be `"low"`, `"medium"`, or `"high"`.
- Invalid values return `400 Bad Request`.

---

### List All Tasks

```
GET /tasks
```

**Response (200):**
```json
[
  {
    "id": 1,
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "mp4",
    "quality": "medium",
    "status": "completed",
    "file_path": "/path/to/backend/downloads/task_1_video.mp4",
    "error_message": null,
    "created_at": "2025-04-07T10:00:00",
    "updated_at": "2025-04-07T10:02:30"
  }
]
```

Tasks are ordered by `created_at DESC` (newest first).

---

### Get Single Task

```
GET /tasks/{task_id}
```

**Response (200):** Same object as in the list response.

**Response (404):**
```json
{ "detail": "Task not found" }
```

---

### Download File

```
GET /download/{task_id}
```

Returns the file as an `application/octet-stream` download.

**Error responses:**
- `404` — Task not found.
- `400` — File not ready yet (task is not `COMPLETED`).
- `404` — File not found on server (task is `COMPLETED` but file was deleted from disk).

---

### Parse Natural Language Message

```
POST /llm/parse
```

**Request Body:**
```json
{
  "message": "download this video as MP4: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response (200):**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4",
  "quality": "high",
  "search_query": null,
  "original_message": "download this video as MP4: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**How it works:**
1. If `QWEN_API_KEY` is set, the message is sent to the configured LLM endpoint with a system prompt that instructs the model to return structured JSON.
2. If the LLM call fails or no API key is set, a **regex-based fallback** parses the message for URLs, format keywords (`mp3`, `mp4`, `audio`, `video`), and quality keywords (`high`, `low`).
3. If no URL is found, the remaining text (minus stopwords) is returned as `search_query`.

---

### Static Files (Web Interface)

| Path | Content |
|---|---|
| `GET /` | `frontend/index.html` |
| `GET /style.css` | `frontend/style.css` |
| `GET /app.js` | `frontend/app.js` |

---

## Using the Web Interface

The web interface is a single-page application with three main sections:

### 1. Manual Download Form (Left Column)

| Field | Description |
|---|---|
| **URL** | Paste a YouTube or VK video URL. |
| **Format** | Select **MP3** (audio only) or **MP4** (video). |
| **Quality** | Select **Low**, **Medium**, or **High**. |
| **Start Download** | Submits the request and creates a task. |

### 2. AI Chat Assistant (Right Column)

Type natural language requests. The assistant will:

- Extract the URL, format, and quality from your message.
- Fill in the download form fields automatically.
- Confirm the parsed result with a message.

**Example messages that work:**

| Message | Parsed Result |
|---|---|
| `download this video as MP4: https://youtube.com/...` | URL + mp4 |
| `save audio from https://vk.com/video...` | URL + mp3 |
| `get me this in high quality mp3: https://...` | URL + mp3 + high |
| `download lofi hip hop radio` | search_query = "lofi hip hop radio" |

### 3. Task List (Bottom)

Displays all download tasks with:

- **Task ID** and **status badge** (color-coded: blue=pending, yellow=downloading, green=completed, red=failed).
- **Format** and **quality** info.
- **Created** and **updated** timestamps.
- **Download button** for completed tasks.
- **Error message** for failed tasks.

The task list **auto-refreshes every 3 seconds**. No page reload needed.

---

## Known Limitations (v1)

| # | Limitation | Workaround / Notes |
|---|---|---|
| 1 | **No URL validation** — The backend passes the URL directly to yt-dlp without pre-validation. Invalid URLs result in a failed task with a yt-dlp error. | The error message in the task list shows the root cause. |
| 2 | **Medium and High quality map to the same yt-dlp setting** (`best`). | Use `low` to get the `worst` quality. True resolution-specific selection is planned for v2. |
| 3 | **Search functionality is not implemented** — If no URL is provided, the `search_query` is extracted but no actual search is performed. | Users must provide a direct URL. |
| 4 | **No file cleanup** — Completed and failed download files accumulate in `backend/downloads/`. | Manually delete files or implement a cron job. |
| 5 | **No authentication** — All endpoints are public. | Suitable for personal/local use only. |
| 6 | **No download progress bar** — Status jumps from `DOWNLOADING` to `COMPLETED` with no intermediate percentage. | Planned for v2. |
| 7 | **LLM defaults inconsistency** — `llm_parser.py` has its own hardcoded defaults for `LLM_API_URL` and `LLM_MODEL` that differ from `config.py`. | Always set these variables explicitly in your `.env` file. |
| 8 | **VK geo-restrictions** — Some VK videos may be unavailable depending on server location. | Test with known-public VK videos. |

---

## Planned for v2

- [ ] **Real search integration** — Use yt-dlp search or a third-party API to find videos by query.
- [ ] **Download progress tracking** — Real-time progress percentage via WebSockets.
- [ ] **File cleanup** — Automatic deletion of files older than N days.
- [ ] **Authentication** — User accounts with API key or session-based auth.
- [ ] **Resolution-specific quality** — Allow users to pick specific resolutions (360p, 720p, 1080p).
- [ ] **Batch downloads** — Submit multiple URLs at once.
- [ ] **Docker compose for the backend** — Full containerization of the FastAPI app alongside PostgreSQL.
- [ ] **Unified LLM configuration** — Resolve the discrepancy between `config.py` and `llm_parser.py` defaults.
- [ ] **Rate limiting** — Prevent abuse with per-IP or per-user request limits.
- [ ] **Unit & integration tests** — Full test suite with pytest.

---

## Troubleshooting

### Server won't start

**Problem:** `uvicorn` fails with an import or module error.

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
# Ensure you run from the backend/ directory:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Database connection error

**Problem:** `sqlalchemy.exc.OperationalError: could not connect to server`.

**Solution:**
```bash
# Check that the PostgreSQL container is running:
docker ps | grep postgres

# If not running, start it:
cd backend && docker-compose up -d

# Verify the DATABASE_URL in .env matches the docker-compose credentials.
```

---

### ffmpeg not found

**Problem:** MP3 downloads fail with `ffmpeg not found` or `ffprobe/avconv not found`.

**Solution:**
```bash
# Install ffmpeg:
sudo apt install -y ffmpeg

# Verify:
ffmpeg -version
```

---

### yt-dlp errors with "Unsupported URL"

**Problem:** Download fails with an unsupported URL error.

**Solution:**
- Ensure the URL is a valid YouTube or VK URL.
- Update yt-dlp: `pip install --upgrade yt-dlp`.
- Some URLs (e.g., playlists, Shorts, or live streams) may not be fully supported.

---

### LLM chat doesn't parse messages correctly

**Problem:** The chat assistant always uses the regex fallback or returns empty fields.

**Solution:**
- If you want LLM-based parsing, set `QWEN_API_KEY` and verify `LLM_API_URL` is accessible:
  ```bash
  curl -H "X-API-Key: $QWEN_API_KEY" -X POST "$LLM_API_URL" -d '{"model":"qwen2:0.5b","prompt":"test"}'
  ```
- The regex fallback should still handle basic patterns like `mp3`, `mp4`, `high`, `low`, and URLs.

---

### Task stuck in DOWNLOADING state

**Problem:** A task remains in `DOWNLOADING` for a very long time or never completes.

**Solution:**
- Large files or slow network connections can cause long download times.
- Check the backend logs for errors: `tail -f backend/logs/uvicorn.log` (if logging is configured).
- If the task is truly stuck, restart the server. The task will remain in its last committed state.

---

### CORS errors in browser console

**Problem:** Frontend fetch calls fail with CORS errors.

**Solution:**
- CORS is configured to allow all origins (`allow_origens=["*"]`) in `main.py`. If you see CORS errors, ensure the frontend is being served from the **same origin** as the backend (i.e., access the app via `http://<server>:8000/`, not by opening `index.html` directly from the file system).

---

## Project Structure

```
MediaFetch/
├── .env.example            # Environment variables template
├── .gitignore
├── README.md               # This file
├── docs/
│   └── TESTING-INSTRUCTIONS.md
├── backend/
│   ├── docker-compose.yml  # PostgreSQL container
│   ├── requirements.txt    # Python dependencies
│   └── app/
│       ├── __init__.py
│       ├── config.py       # Pydantic settings
│       ├── database.py     # SQLAlchemy setup
│       ├── main.py         # FastAPI app & routes
│       ├── models.py       # ORM models
│       ├── schemas.py      # Pydantic schemas
│       ├── services/
│       │   ├── downloader.py   # yt-dlp wrapper
│       │   └── llm_parser.py   # LLM + regex parser
│       └── routes/
│           └── __init__.py
│   └── downloads/          # Downloaded files stored here
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

---

## Testing

For detailed step-by-step testing instructions, see [docs/TESTING-INSTRUCTIONS.md](docs/TESTING-INSTRUCTIONS.md).

Quick smoke test:

```bash
# 1. Health check
curl http://localhost:8000/api/health

# 2. Create a download task
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","format":"mp4","quality":"medium"}'

# 3. List tasks
curl http://localhost:8000/tasks

# 4. Parse a natural language message
curl -X POST http://localhost:8000/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"message":"download this as mp3: https://youtube.com/watch?v=abc123"}'
```

---

## License

This project is provided as-is for educational and personal use.
