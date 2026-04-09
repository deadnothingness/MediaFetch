# MediaFetch

> Download audio (MP3) and video (MP4) from VK by URL with real-time progress tracking and AI chat assistant.

## Demo

![Screenshot](docs/screenshot.png)

## Product Context

### End Users

Students, educators, and anyone who needs to save online media (lectures, music, tutorials) for offline access without ads or third-party download sites.

### Problem

Downloading from VK requires navigating ad-heavy websites or using unreliable browser extensions. Users need a simple, clean interface to save media with one click.

### Solution

A web-based service that accepts a VK video URL, lets users choose format (MP3/MP4) and quality (360p-1080p / 128k-320k), and downloads the file with real-time progress tracking. An AI chat assistant can parse natural language requests to auto-fill the form.

## Features

### Implemented (v2)

- ✅ Download MP3 (audio) from VK by URL
- ✅ Download MP4 (video) from VK by URL
- ✅ Resolution-specific quality (360p, 720p, 1080p, best)
- ✅ Audio bitrate selection (128k, 192k, 320k)
- ✅ Real-time download progress bar (SSE)
- ✅ Smart file naming (uses video title, not task ID)
- ✅ Task list with status tracking
- ✅ AI chat assistant (Qwen API + regex fallback)
- ✅ Docker deployment with persistent storage

### Not Yet Implemented

- ⬜ YouTube support (network restricted on university VMs)
- ⬜ Batch downloads (multiple URLs at once)
- ⬜ User authentication
- ⬜ Download history per user
- ⬜ File cleanup (automatic deletion of old files)

## Usage

1. Open `http://localhost:8000` in your browser
2. Paste a VK video URL (e.g., `https://vkvideo.ru/video-xxxxx_xxxxx`)
3. Select format: **MP4 (Video)** or **MP3 (Audio)**
4. Select quality:
   - For video: 360p, 720p, 1080p, Best
   - For audio: 128k, 192k, 320k
5. Click **Start Download**
6. Watch progress bar fill, then click **Download File** when complete

### AI Chat Assistant

Type natural language requests in the chat widget, e.g.:

- `"download this video as MP4: https://vkvideo.ru/video-..."`
- `"save audio from this link in high quality"`

The assistant will auto-fill the form – just click Start Download.

## Deployment

### Requirements

- **OS:** Ubuntu 24.04 (or any Linux with Docker support)
- **CPU:** 2+ cores
- **RAM:** 4+ GB
- **Disk:** 10+ GB free space
- **Network:** Access to VK (no VPN required)

### Prerequisites on VM

```bash
# Install Docker and Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in

# Install ffmpeg (required for audio conversion)
sudo apt install -y ffmpeg
