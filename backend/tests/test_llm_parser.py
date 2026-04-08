"""Tests for LLM parser (regex fallback only, to avoid real API calls)."""
import pytest
from app.services.llm_parser import simple_parse


@pytest.mark.parametrize("message,expected_url,expected_format,expected_quality,expected_search", [
    ("download this video: https://youtu.be/abc123", "https://youtu.be/abc123", "mp4", "medium", None),
    ("save audio from https://vk.com/video-123 in high quality", "https://vk.com/video-123", "mp3", "high", None),
    ("get me this as mp4: https://youtube.com/watch?v=xyz low quality", "https://youtube.com/watch?v=xyz", "mp4", "low", None),
    ("download lofi hip hop radio", None, None, "medium", "lofi hip hop radio"),
    ("mp3 please", None, "mp3", "medium", None),
    ("video high quality", None, "mp4", "high", None),
])
def test_simple_parse(message, expected_url, expected_format, expected_quality, expected_search):
    result = simple_parse(message)
    assert result["url"] == expected_url
    assert result["format"] == expected_format
    assert result["quality"] == expected_quality
    assert result["search_query"] == expected_search