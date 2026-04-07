# MediaFetch — Implementation Plan

---

## Product Vision

A web service that lets users download audio (MP3) and video (MP4) from YouTube and VK by URL, with an **AI chat assistant** that understands natural language requests.

---

## Version 1 — Core Feature: Download by URL with AI Assistant

### Scope

**One core thing done well:** Download media from a direct URL in the user's chosen format and quality, with an AI chat assistant that parses natural language requests.

| Component | Implementation | Status |
|---|---|---|
| **Backend** | FastAPI app with `/download`, `/tasks`, `/download/{task_id}`, `/llm/parse`, `/api/health` endpoints. Background task processing with yt-dlp + ffmpeg. Dockerized with a `Dockerfile` + `docker-compose.yml`. | Implemented |
| **Database** | PostgreSQL (via Docker Compose). Stores `DownloadTask` records with status lifecycle: `PENDING → DOWNLOADING → COMPLETED / FAILED`. | Implemented |
| **Client** | Single-page web app (HTML/CSS/JS) with two-column layout: manual download form + AI chat widget. Auto-refreshing task list (every 3 s). | Implemented |

### Core Feature Breakdown

| Feature | Description | Status |
|---|---|---|
| **Download by URL** | User pastes a YouTube or VK URL, selects MP3/MP4 and quality (low/medium/high), and starts download. | Implemented |
| **Task tracking** | Each download is a task with real-time status updates visible in the task list. | Implemented |
| **File delivery** | Completed files are served directly from the backend via `GET /download/{task_id}`. | Implemented |
| **AI chat assistant** | User types a natural language request → `/llm/parse` extracts URL, format, quality → form fields are auto-filled. Uses Qwen API with regex fallback. | Implemented |
| **Error handling** | Failed tasks store the error message and display it in the UI. | Implemented |

### Known Limitations (v1)

1. Medium and High quality both map to `best` in yt-dlp.
2. No actual search — if no URL is provided, only the `search_query` is extracted.
3. No download progress bar (status jumps from DOWNLOADING to COMPLETED).
4. No authentication — all endpoints are public.
5. No file cleanup — files accumulate in `backend/downloads/`.
6. `llm_parser.py` has hardcoded defaults that differ from `config.py`.

### Deliverable for TA

- A running web app at `http://<server-ip>:8000`.
- The TA can:
  1. Paste a YouTube/VK URL, pick format/quality, and download a file.
  2. Type a natural language request in the chat and see the form auto-filled.
  3. Watch task status update in real time.
  4. Download the completed file.
- Accompanied by [TESTING-INSTRUCTIONS.md](TESTING-INSTRUCTIONS.md) and [README.md](../README.md).

---

## Version 2 — Build Upon v1

### Scope

Improve the core download experience, add **download progress tracking** (the most impactful feature gap from v1), and address TA feedback.

### Planned Improvements

| Feature | Description | Priority |
|---|---|---|
| **Real-time download progress** | WebSockets or Server-Sent Events (SSE) push progress percentage from the backend to the frontend during download. Replaces the binary DOWNLOADING → COMPLETED jump. | High |
| **Resolution-specific quality** | Let users pick specific video resolutions (360p, 720p, 1080p) instead of the current low/medium/high that maps poorly. | High |
| **File cleanup** | Automatic deletion of files older than N days (configurable via env var). A cron job or scheduled FastAPI task. | Medium |
| **Resolve LLM config discrepancy** | Unify `llm_parser.py` to read from `config.py` instead of having its own hardcoded defaults. | Medium |
| **Download progress in CLI / API** | Expose progress via a `/tasks/{task_id}/progress` endpoint for API consumers. | Medium |
| **TA feedback implementation** | Address any issues, bug reports, or suggestions raised during the v1 demo. | High |

### Deployment (v2)

- **Production-ready server** — Gunicorn + Uvicorn workers, systemd service, optional Nginx reverse proxy.
- **Public URL** — Deployed on the university VM and accessible via domain or IP.

### What Stays the Same

- Core architecture (FastAPI + PostgreSQL + vanilla JS frontend).
- yt-dlp + ffmpeg for media downloading.
- Two-column UI layout (form + chat).
- LLM parsing with regex fallback.

---

## Component Checklist

### Version 1

| Component | Useful? | Notes |
|---|---|---|
| Backend | Yes | Handles downloads, task management, LLM parsing, file serving. |
| Database | Yes | Persists task state across server restarts; enables task list and status tracking. |
| Web app | Yes | Users interact with the form, chat, and task list. Fully functional. |

### Version 2

| Component | Useful? | Notes |
|---|---|---|
| Backend | Yes | Adds progress tracking, better quality selection, file cleanup. |
| Database | Yes | Stores progress state, cleanup schedules. |
| Web app | Yes | Shows real-time progress bars, resolution picker. |

---

## Constraints

| Constraint | Impact |
|---|---|
| **No Telegram bots** | Blocked on university VMs. Web app is the delivery channel. |
| **Lab 8 setup optional** | Can use the existing FastAPI + Docker setup or start from scratch. We use the existing one. |
| **v1 must be a functioning product** | Not a prototype — it downloads real files from real URLs and delivers them to the user. |

---

## Timeline Overview

```
v1 ─────────────────────────────►  TA demo & feedback
      Implement  │  Test  │  Document  │  Show
v2 ───────────────────────────────────────────►  Deploy & publish
      Address feedback  │  Add features  │  Dockerize  │  Deploy
```
