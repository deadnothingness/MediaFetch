# MediaFetch

MediaFetch is a service that lets you download audio and video from VK and YouTube — either by direct link or by searching content by name. It provides a clean web interface and a Telegram bot, supports format and quality selection (MP3, MP4, etc.), and tracks download tasks. Optionally integrated with an LLM agent to parse natural language requests.

## Features

- Download by URL or search query
- Choose output format (MP3 / MP4) and quality
- Web UI + Telegram bot interfaces
- Task queue and history
- Dockerized (FastAPI + PostgreSQL + yt-dlp)
