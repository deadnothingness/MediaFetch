# MediaFetch v1 — Testing Instructions

> **Audience:** Manual testers, teaching assistants, or reviewers.
> **Purpose:** Step-by-step guide to verify that all core features of MediaFetch v1 work as expected.

---

## Table of Contents

- [MediaFetch v1 — Testing Instructions](#mediafetch-v1--testing-instructions)
  - [Table of Contents](#table-of-contents)
  - [1. Prerequisites](#1-prerequisites)
    - [Verify the backend is reachable](#verify-the-backend-is-reachable)
  - [2. How to Run the Application](#2-how-to-run-the-application)
    - [Quick start (local development)](#quick-start-local-development)
    - [Access the web interface](#access-the-web-interface)
  - [3. Test Cases](#3-test-cases)
    - [TC-1: Download YouTube Video as MP4](#tc-1-download-youtube-video-as-mp4)
    - [TC-2: Download YouTube Audio as MP3](#tc-2-download-youtube-audio-as-mp3)
    - [TC-3: Download VK Video as MP4](#tc-3-download-vk-video-as-mp4)
    - [TC-4: Download VK Audio as MP3](#tc-4-download-vk-audio-as-mp3)
    - [TC-5: Quality Selection (Low / Medium / High)](#tc-5-quality-selection-low--medium--high)
    - [TC-6: Task List Status Updates](#tc-6-task-list-status-updates)
    - [TC-7: File Download After Completion](#tc-7-file-download-after-completion)
    - [TC-8: Chat Assistant — Natural Language Parsing](#tc-8-chat-assistant--natural-language-parsing)
    - [TC-9: Chat Assistant — Search Query Extraction](#tc-9-chat-assistant--search-query-extraction)
    - [TC-10: Error Handling — Invalid URL](#tc-10-error-handling--invalid-url)
    - [TC-11: Error Handling — Missing ffmpeg](#tc-11-error-handling--missing-ffmpeg)
    - [TC-12: Error Handling — Unreachable URL / Network Error](#tc-12-error-handling--unreachable-url--network-error)
    - [TC-13: Health Check Endpoint](#tc-13-health-check-endpoint)
    - [TC-14: Task Not Found (404)](#tc-14-task-not-found-404)
  - [4. How to Report Bugs](#4-how-to-report-bugs)
    - [Bug Report Template](#bug-report-template)
    - [Severity Definitions](#severity-definitions)
    - [Where to Submit](#where-to-submit)
  - [Appendix A — API Quick Reference](#appendix-a--api-quick-reference)
  - [Appendix B — Environment Variables](#appendix-b--environment-variables)

---

## 1. Prerequisites

Before starting, ensure the following are in place:

| Requirement | Details |
|---|---|
| **Backend server running** | FastAPI app accessible at `http://<server-ip>:8000` (locally: `http://localhost:8000`). |
| **Database running** | PostgreSQL container (via `docker-compose.yml`) or SQLite if configured. |
| **yt-dlp installed** | Available in the backend Python environment (`pip install yt-dlp`). |
| **ffmpeg installed** | Required for MP3 conversion. Test with `ffmpeg -version`. |
| **Modern browser** | Chrome, Firefox, Edge, or Safari (latest versions). |
| **Test URLs** | Have at least one working YouTube video URL and one working VK video URL ready. |
| **(Optional) LLM API running** | If testing the AI chat with LLM tier 1, ensure the Qwen/Ollama endpoint is accessible. If not, the regex fallback will be used automatically. |

### Verify the backend is reachable

```bash
curl http://localhost:8000/api/health
# Expected: {"status":"ok"}
```

---

## 2. How to Run the Application

### Quick start (local development)

```bash
# 1. Start the database
cd backend
docker-compose up -d

# 2. Set up the virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and optional LLM settings

# 4. Start the backend server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access the web interface

Open a browser and navigate to:

```
http://localhost:8000
```

You should see a two-column layout:
- **Left column:** Manual download form.
- **Right column:** AI chat widget.
- **Below both:** Task list section.

---

## 3. Test Cases

Each test case follows this format:

| Field | Description |
|---|---|
| **ID** | Unique test case identifier. |
| **Title** | Short description. |
| **Preconditions** | What must be true before starting. |
| **Steps** | Numbered actions to perform. |
| **Expected Result** | What should happen. |
| **Pass / Fail** | Fill in during execution. |

---

### TC-1: Download YouTube Video as MP4

| | |
|---|---|
| **Title** | Download a YouTube video in MP4 format. |
| **Preconditions** | Backend is running; you have a valid YouTube video URL. |
| **Steps** | 1. Open `http://localhost:8000`. <br> 2. In the **URL** field of the download form, paste a YouTube video URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`). <br> 3. Select **Format: MP4**. <br> 4. Select **Quality: Medium**. <br> 5. Click **Start Download**. |
| **Expected Result** | - A success toast/notification appears with a **Task ID**. <br> - The task appears in the task list below with status **PENDING**, then transitions to **DOWNLOADING**, and finally to **COMPLETED** (auto-refreshes every 3 seconds). <br> - A **Download** button appears next to the completed task. <br> - Clicking **Download** saves an `.mp4` file to your computer. |
| **Pass / Fail** | ☐ |

---

### TC-2: Download YouTube Audio as MP3

| | |
|---|---|
| **Title** | Download audio from a YouTube video in MP3 format. |
| **Preconditions** | Backend is running; ffmpeg is installed; you have a valid YouTube video URL. |
| **Steps** | 1. Open `http://localhost:8000`. <br> 2. Paste a YouTube URL in the **URL** field. <br> 3. Select **Format: MP3**. <br> 4. Select **Quality: High**. <br> 5. Click **Start Download**. |
| **Expected Result** | - Task is created and progresses through **PENDING → DOWNLOADING → COMPLETED**. <br> - The downloaded file is an `.mp3` audio file. <br> - The file plays correctly in a media player. |
| **Pass / Fail** | ☐ |

---

### TC-3: Download VK Video as MP4

| | |
|---|---|
| **Title** | Download a VK video in MP4 format. |
| **Preconditions** | Backend is running; you have a valid VK video URL. |
| **Steps** | 1. Open `http://localhost:8000`. <br> 2. Paste a VK video URL (e.g., `https://vk.com/video-12345_67890`) in the **URL** field. <br> 3. Select **Format: MP4**. <br> 4. Select **Quality: High**. <br> 5. Click **Start Download**. |
| **Expected Result** | - Task is created and completes successfully. <br> - The downloaded file is an `.mp4` video. |
| **Pass / Fail** | ☐ |



---

### TC-4: Download VK Audio as MP3

| | |
|---|---|
| **Title** | Download audio from a VK video in MP3 format. |
| **Preconditions** | Backend is running; ffmpeg is installed; you have a valid VK video URL. |
| **Steps** | 1. Open `http://localhost:8000`. <br> 2. Paste a VK video URL in the **URL** field. <br> 3. Select **Format: MP3**. <br> 4. Select **Quality: Medium**. <br> 5. Click **Start Download**. |
| **Expected Result** | - Task completes successfully. <br> - The downloaded file is an `.mp3` audio file. |
| **Pass / Fail** | ☐ |

---

### TC-5: Quality Selection (Low / Medium / High)

| | |
|---|---|
| **Title** | Verify that quality selection affects the downloaded file. |
| **Preconditions** | Backend is running; you have a valid YouTube URL with multiple quality variants. |
| **Steps** | 1. Submit the same YouTube URL three times, once with each quality setting (**Low**, **Medium**, **High**), all as **MP4**. <br> 2. Wait for all three tasks to complete. <br> 3. Download all three files. <br> 4. Compare file sizes (and optionally resolution via `ffprobe`). |
| **Expected Result** | - All three tasks complete successfully. <br> - **High** quality file is ≥ **Medium** quality file in size. <br> - **Low** quality file is ≤ **Medium** quality file in size. <br> - File resolutions reflect the quality differences (verifiable via `ffprobe -v error -show_entries stream=width,height -of csv <file>`). |
| **Pass / Fail** | ☐ |

> **Note:** In the current implementation, `medium` and `high` both map to `best` in yt-dlp. The `low` setting maps to `worst`. If file sizes are identical for medium and high, this is a **known limitation** of v1, not a bug.

---

### TC-6: Task List Status Updates

| | |
|---|---|
| **Title** | Verify that the task list correctly shows status transitions. |
| **Preconditions** | Backend is running; you have a valid URL for a large file (to observe status changes). |
| **Steps** | 1. Submit a download for a relatively large file (to increase the time in the DOWNLOADING state). <br> 2. Watch the task list section closely. <br> 3. Observe the status badge change over time. |
| **Expected Result** | - The task initially appears with status **PENDING** (may be very brief). <br> - Status changes to **DOWNLOADING** within a few seconds. <br> - Status eventually changes to **COMPLETED** (green badge) or **FAILED** (red badge). <br> - The task list auto-refreshes every 3 seconds without requiring a page reload. |
| **Pass / Fail** | ☐ |

---

### TC-7: File Download After Completion

| | |
|---|---|
| **Title** | Verify that completed tasks allow file download. |
| **Preconditions** | At least one task in **COMPLETED** status. |
| **Steps** | 1. Locate the completed task in the task list. <br> 2. Click the **Download** button. |
| **Expected Result** | - The browser initiates a file download. <br> - The file is saved to the default download location. <br> - The file opens correctly (video plays or audio plays). <br> - The filename includes the task ID (e.g., `task_3_VideoTitle.mp4`). |
| **Pass / Fail** | ☐ |

---

### TC-8: Chat Assistant — Natural Language Parsing

| | |
|---|---|
| **Title** | Verify that the chat assistant parses natural language download requests. |
| **Preconditions** | Backend is running. LLM API may or may not be configured (regex fallback should work regardless). |
| **Steps** | **Test 8a — Video download:** <br> 1. In the chat widget, type: `download this video as MP4: https://www.youtube.com/watch?v=dQw4w9WgXcQ` <br> 2. Press **Send**. <br> 3. Observe the bot response and the form fields. <br><br> **Test 8b — Audio download:** <br> 4. Type: `save audio from https://www.youtube.com/watch?v=dQw4w9WgXcQ` <br> 5. Press **Send**. <br> 6. Observe the bot response and the form fields. <br><br> **Test 8c — Quality specified:** <br> 7. Type: `get me this in high quality mp3: https://www.youtube.com/watch?v=dQw4w9WgXcQ` <br> 8. Press **Send**. |
| **Expected Result** | **Test 8a:** <br> - The URL field in the form is filled with the YouTube URL. <br> - Format is set to **MP4**. <br> - Bot replies with a confirmation message like "Got it! I've filled in the download form…". <br><br> **Test 8b:** <br> - The URL field is filled. <br> - Format is set to **MP3**. <br> - Bot confirms. <br><br> **Test 8c:** <br> - The URL field is filled. <br> - Format is set to **MP3**. <br> - Quality is set to **High**. <br> - Bot confirms. |
| **Pass / Fail** | ☐ |

---

### TC-9: Chat Assistant — Search Query Extraction

| | |
|---|---|
| **Title** | Verify that the chat assistant extracts a search query when no URL is provided. |
| **Preconditions** | Backend is running. |
| **Steps** | 1. In the chat widget, type: `download lofi hip hop radio` <br> 2. Press **Send**. <br> 3. Observe the form fields and bot response. |
| **Expected Result** | - The **URL** field in the form may be empty. <br> - The `search_query` field in the parsed result should contain `"lofi hip hop radio"`. <br> - The bot should acknowledge the request (e.g., "I understand you want to search for…"). <br> - **Note:** Actual search functionality is **not implemented in v1**. This test only verifies that the query is extracted and stored — not that results are returned. |
| **Pass / Fail** | ☐ |

---

### TC-10: Error Handling — Invalid URL

| | |
|---|---|
| **Title** | Verify that the system handles invalid URLs gracefully. |
| **Preconditions** | Backend is running. |
| **Steps** | 1. Open `http://localhost:8000`. <br> 2. In the **URL** field, enter an invalid string (e.g., `not-a-valid-url` or `https://this-domain-definitely-does-not-exist-xyz123.com/video`). <br> 3. Select **Format: MP4**, **Quality: Medium**. <br> 4. Click **Start Download**. |
| **Expected Result** | - A task is created. <br> - The task transitions to **DOWNLOADING** and then to **FAILED**. <br> - The task list shows a red **FAILED** badge. <br> - An **error message** is displayed (e.g., "Unsupported URL" or "ERROR: …"). <br> - The application does **not** crash. |
| **Pass / Fail** | ☐ |

---

### TC-11: Error Handling — Missing ffmpeg

| | |
|---|---|
| **Title** | Verify behavior when ffmpeg is not installed (required for MP3 conversion). |
| **Preconditions** | Backend is running; **ffmpeg is NOT installed** on the system. To simulate, temporarily rename the ffmpeg binary: `sudo mv /usr/bin/ffmpeg /usr/bin/ffmpeg.bak`. |
| **Steps** | 1. Submit a download request with **Format: MP3** for any valid YouTube URL. <br> 2. Wait for the task to process. |
| **Expected Result** | - The task transitions to **FAILED**. <br> - The error message mentions ffmpeg (e.g., "ffmpeg not found" or "ffprobe/avconv not found"). <br> - The application does **not** crash. <br> - **After testing:** Restore ffmpeg: `sudo mv /usr/bin/ffmpeg.bak /usr/bin/ffmpeg`. |
| **Pass / Fail** | ☐ |

---

### TC-12: Error Handling — Unreachable URL / Network Error

| | |
|---|---|
| **Title** | Verify behavior when the target URL is unreachable (network timeout). |
| **Preconditions** | Backend is running. |
| **Steps** | 1. Use a URL that will cause a timeout or connection error. For example, use a valid URL pattern but with a private IP: `https://192.0.2.1/watch?v=test`. <br> 2. Submit the download request. |
| **Expected Result** | - The task transitions to **FAILED**. <br> - An appropriate error message is displayed. <br> - The application does **not** crash or hang indefinitely. |
| **Pass / Fail** | ☐ |

---

### TC-13: Health Check Endpoint

| | |
|---|---|
| **Title** | Verify the health check API returns a valid response. |
| **Preconditions** | Backend is running. |
| **Steps** | 1. Run: `curl http://localhost:8000/api/health` |
| **Expected Result** | - Response body: `{"status":"ok"}`. <br> - HTTP status code: `200`. |
| **Pass / Fail** | ☐ |

---

### TC-14: Task Not Found (404)

| | |
|---|---|
| **Title** | Verify that requesting a non-existent task returns a 404. |
| **Preconditions** | Backend is running. |
| **Steps** | 1. Run: `curl http://localhost:8000/tasks/999999` (use an ID that does not exist). |
| **Expected Result** | - HTTP status code: `404`. <br> - Response body contains `"Task not found"`. |
| **Pass / Fail** | ☐ |

---

## 4. How to Report Bugs

When reporting issues, use the following format:

### Bug Report Template

```
**Test Case ID:** TC-XX
**Title:** Brief description of the issue
**Severity:** Critical / Major / Minor / Cosmetic
**Environment:**
  - OS: Ubuntu 24.04 / Windows 11 / macOS 15.x
  - Browser: Chrome 131 / Firefox 133
  - Backend version: v1.0.0
  - Python version: 3.12.x

**Steps to Reproduce:**
1. ...
2. ...
3. ...

**Expected Result:**
What should have happened.

**Actual Result:**
What actually happened.

**Screenshots / Logs:**
Attach any screenshots or console output that may help.

**Additional Notes:**
Any other relevant information.
```

### Severity Definitions

| Level | Description |
|---|---|
| **Critical** | Application crashes, data loss, core feature completely broken. |
| **Major** | Feature does not work as specified but a workaround exists. |
| **Minor** | Feature works with minor deviations from expected behavior. |
| **Cosmetic** | UI/UX issues (typo, misalignment, color mismatch). |

### Where to Submit

- Create an issue in the project's issue tracker (GitHub / GitLab / etc.).
- Or send bug reports via email to: **[your-email@example.com]**.

---

## Appendix A — API Quick Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web interface (HTML page). |
| `GET` | `/api/health` | Health check. Returns `{"status": "ok"}`. |
| `POST` | `/download` | Create a download task. Body: `{ "url": str, "format": "mp3"\|"mp4", "quality": "low"\|"medium"\|"high" }`. |
| `GET` | `/tasks` | List all tasks. |
| `GET` | `/tasks/{task_id}` | Get a single task. Returns 404 if not found. |
| `GET` | `/download/{task_id}` | Download the file for a completed task. |
| `POST` | `/llm/parse` | Parse a natural language message. Body: `{ "message": str }`. |

See [README.md](../README.md) for detailed examples.

---

## Appendix B — Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | `postgresql://mediafetch:mediafetch123@localhost:5432/mediafetch_db` | Database connection string. |
| `LLM_API_URL` | No | `http://localhost:11434/api/generate` | URL for the LLM API endpoint. |
| `LLM_MODEL` | No | `qwen2:0.5b` | Model name for the LLM. |
| `QWEN_API_KEY` | No | _(empty)_ | API key for the LLM service. If empty, regex fallback is used. |

---

*End of Testing Instructions.*
