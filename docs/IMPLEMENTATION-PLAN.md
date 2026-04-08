# MediaFetch — Implementation Plan

---

## Product Vision

A web service that lets users download audio (MP3) and video (MP4) from YouTube and VK by URL, with an **AI chat assistant** that understands natural language requests.

---

## Version 1 — Core Feature: Download by URL with AI Assistant

### Scope

**One core thing done well:** Download media from a direct URL in the user’s chosen format and quality, with an AI chat assistant that parses natural language requests.

| Component | Implementation | Status |
| ----------- | ---------------- | -------- |
| **Backend** | FastAPI app with `/download`, `/tasks`, `/download/{task_id}`, `/llm/parse`, `/api/health` endpoints. Background task processing with yt‑dlp + ffmpeg. Dockerized with a `Dockerfile` + `docker-compose.yml`. | Implemented |
| **Database** | PostgreSQL (via Docker Compose). Stores `DownloadTask` records with status lifecycle: `PENDING → DOWNLOADING → COMPLETED / FAILED`. | Implemented |
| **Client** | Single‑page web app (HTML/CSS/JS) with two‑column layout: manual download form + AI chat widget. Auto‑refreshing task list (every 3 s). | Implemented |

### Core Feature Breakdown

| Feature | Description | Status |
| --------- | ------------- | -------- |
| **Download by URL** | User pastes a YouTube or VK URL, selects MP3/MP4 and quality (low/medium/high), and starts download. | Implemented |
| **Task tracking** | Each download is a task with real‑time status updates visible in the task list. | Implemented |
| **File delivery** | Completed files are served directly from the backend via `GET /download/{task_id}`. | Implemented |
| **AI chat assistant** | User types a natural language request → `/llm/parse` extracts URL, format, quality → form fields are auto‑filled. Uses Qwen API with regex fallback. | Implemented |
| **Error handling** | Failed tasks store the error message and display it in the UI. | Implemented |

### Known Limitations (v1)

1. Medium and High quality both map to `best` in yt‑dlp.
2. No actual search — if no URL is provided, only the `search_query` is extracted.
3. No download progress bar — status jumps from `DOWNLOADING` to `COMPLETED`.
4. No authentication — all endpoints are public.
5. No file cleanup — files accumulate in `backend/downloads/`.
6. `llm_parser.py` has hardcoded defaults that differ from `config.py`.

### Deliverable for TA

- A running web app at `http://<server-ip>:8000`.
- The TA can:
  1. Paste a YouTube/VK URL, pick format/quality, and download a file.
  2. Type a natural language request in the chat and see the form auto‑filled.
  3. Watch task status update in real time.
  4. Download the completed file.
- Accompanied by [TESTING-INSTRUCTIONS.md](TESTING-INSTRUCTIONS.md) and [README.md](../README.md).

---

## Version 2 — Build Upon v1

### Scope

Improve the core download experience, add **download progress tracking**, **resolution‑specific quality**, **real search**, **unified LLM configuration**, **smart file naming**, and a full **test suite** – all based on TA feedback.

### Planned Improvements

| Feature | Description | Priority |
| --------- | ------------- | ---------- |
| **Unified LLM configuration** | Remove `config.py`; read all LLM settings (`LLM_API_URL`, `LLM_MODEL`, `QWEN_API_KEY`) directly from environment variables. Both `llm_parser.py` and the main app use the same source of truth. | High |
| **Real‑time download progress** | Implement Server‑Sent Events (SSE) or WebSockets to push progress percentage from the backend to the frontend. Replaces the binary `DOWNLOADING → COMPLETED` jump with a live progress bar. | High |
| **Resolution‑specific quality** | Replace the ambiguous `low/medium/high` dropdown with concrete video resolutions (360p, 720p, 1080p, best). For audio, offer bitrate options (128k, 192k, 320k). | High |
| **Full test suite (pytest)** | Unit and integration tests covering database models, download task lifecycle, LLM parser (regex fallback), and all API endpoints using FastAPI `TestClient`. Tests must be written before refactoring to ensure stability. | High |
| **Smart file naming** | Downloaded files will use metadata from yt‑dlp to generate readable names. For audio: `Artist - Title.mp3` (or `Channel - Title.mp3` if artist is missing). For video: `Channel - Video Title.mp4`. The generated name is stored in the database and shown in the frontend. | Medium |
| **Real search integration** | Allow users to type a search query (song name, video title) instead of a URL. The backend will use yt‑dlp search (`ytsearch5:query`) to find top results. Users can then pick which result to download. | Medium |
| **File cleanup** | Automatic deletion of downloaded files older than N days (configurable via environment variable). A simple background task (or cron) runs daily. | Medium |
| **Batch downloads** | Allow users to submit multiple URLs or search queries at once (one per line). Each entry becomes a separate task. | Low |
| **Rate limiting** | Use `slowapi` or `redis` to limit requests per IP (e.g., 10 downloads per minute, 100 requests per hour). Useful for production but not required for MVP. | Low |
| **Authentication** | Simple API‑key authentication (user supplies a key in the frontend, stored in `localStorage`). Optional; may be deferred if not needed for the demo. | Low |

### Deployment (v2)

- **Production‑ready server** — Gunicorn + Uvicorn workers, systemd service, optional Nginx reverse proxy.
- **Public URL** — Deployed on the university VM and accessible via domain or IP.
- **Docker** – The existing Dockerfile and `docker-compose.yml` remain; only environment variables are updated.

### What Stays the Same

- Core architecture (FastAPI + PostgreSQL + vanilla JS frontend).
- yt‑dlp + ffmpeg for media downloading.
- Two‑column UI layout (form + chat).
- LLM parsing with regex fallback (now unified configuration).

---

## Component Checklist

### Version 1

| Component | Useful? | Notes |
| ----------- | --------- | ------- |
| Backend | Yes | Handles downloads, task management, LLM parsing, file serving. |
| Database | Yes | Persists task state across server restarts; enables task list and status tracking. |
| Web app | Yes | Users interact with the form, chat, and task list. Fully functional. |

### Version 2

| Component | Useful? | Notes |
| ----------- | --------- | ------- |
| Backend | Yes | Adds progress tracking, resolution selection, search endpoint, unified config. |
| Database | Yes | Stores progress percentage, file names, search history. |
| Web app | Yes | Shows real‑time progress bars, resolution picker, search results UI. |
| Test suite | Yes | Ensures stability during refactoring and new feature development. |

---

## Constraints

| Constraint | Impact |
| ------------ | -------- |
| **No Telegram bots** | Blocked on university VMs. Web app is the delivery channel. |
| **Lab 8 setup optional** | Can use the existing FastAPI + Docker setup or start from scratch. We use the existing one. |
| **v1 must be a functioning product** | Not a prototype — it downloads real files from real URLs and delivers them to the user. |

---

## Timeline Overview

```text
v1 ─────────────────────────────►  TA demo & feedback
      Implement  │  Test  │  Document  │  Show
v2 ───────────────────────────────────────────►  Deploy & publish
      Address feedback  │  Add features  │  Dockerize  │  Deploy
```
