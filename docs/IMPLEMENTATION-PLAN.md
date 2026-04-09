# MediaFetch — Implementation Plan

## Product Vision

A web service that lets users download audio (MP3) and video (MP4) from VK by URL, with an **AI chat assistant** that understands natural language requests.

## Version 1 — Core Feature

**One core thing done well:** Download media from a direct URL in the user's chosen format and quality, with an AI chat assistant that parses natural language requests.

**Status:** ✅ Implemented

**Key features:**

- Download MP3/MP4 by URL
- Task tracking with status updates
- AI chat assistant with regex fallback
- Error handling

## Version 2 — Improvements

**Status:** ✅ Implemented

**Added features:**

- ✅ Real‑time download progress (SSE)
- ✅ Resolution‑specific quality (360p, 720p, 1080p, best)
- ✅ Audio bitrate selection (128k, 192k, 320k)
- ✅ Smart file naming (uses video title)
- ✅ Unified LLM configuration
- ✅ Persistent downloads volume

## What Works

| Feature | Status |
| --------- | -------- |
| Download MP4 from VK | ✅ |
| Download MP3 from VK | ✅ |
| Quality selection (video) | ✅ (360p, 720p, 1080p, best) |
| Quality selection (audio) | ✅ (128k, 192k, 320k) |
| Download progress bar | ✅ (SSE) |
| Task list with auto-refresh | ✅ |
| AI chat assistant | ✅ (Qwen API + regex fallback) |
| Smart file naming | ✅ |
| Docker deployment | ✅ |

## Known Limitations

- YouTube support is disabled due to network restrictions on university VMs
- No search functionality
- No user authentication
- No automatic file cleanup
- No batch downloads

## Deployment

See [README.md](../README.md) for deployment instructions.

## License

MIT
