import os
import re
import json
import httpx
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL", "http://localhost:42005/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "coder-model")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")

SYSTEM_PROMPT = """You are a media download assistant. Extract from user request and return ONLY valid JSON.
Fields: "url" (string or null), "format" ("mp3" or "mp4" or null), "quality" ("low"/"medium"/"high" or null), "search_query" (string or null).
If user asks to search by name (no URL), put the search term in "search_query".
If user says "audio" or "mp3", format should be "mp3". If "video" or "mp4", format "mp4".
Only output JSON, no extra text."""

def simple_parse(user_message: str) -> Dict[str, Any]:
    url_match = re.search(r'https?://[^\s]+', user_message)
    url = url_match.group(0) if url_match else None
    msg_lower = user_message.lower()
    
    format_val = None
    if 'mp3' in msg_lower or 'audio' in msg_lower:
        format_val = 'mp3'
    elif 'mp4' in msg_lower or 'video' in msg_lower:
        format_val = 'mp4'
    
    quality = 'medium'
    if 'high' in msg_lower:
        quality = 'high'
    elif 'low' in msg_lower:
        quality = 'low'
    
    search_query = None
    if not url:
        query = re.sub(r'(download|find|search for|get|save|please|the|this|video|audio|as|in|quality|high|low|medium|mp3|mp4)', '', msg_lower)
        query = re.sub(r'[^\w\s]', '', query).strip()
        if query:
            search_query = query
    
    return {
        "url": url,
        "format": format_val,
        "quality": quality,
        "search_query": search_query
    }

async def parse_request(user_message: str) -> Dict[str, Any]:
    # Try Qwen if configured
    if QWEN_API_KEY and LLM_API_URL:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    LLM_API_URL,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {QWEN_API_KEY}",   # исправлено
                    },
                    json={
                        "model": LLM_MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_message}
                        ],
                        "stream": False,
                        "temperature": 0.1,
                        "max_tokens": 200
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    llm_output = data["choices"][0]["message"]["content"]
                    start = llm_output.find('{')
                    end = llm_output.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = llm_output[start:end]
                        parsed = json.loads(json_str)
                        return {
                            "url": parsed.get("url"),
                            "format": parsed.get("format"),
                            "quality": parsed.get("quality") or "medium",
                            "search_query": parsed.get("search_query")
                        }
        except Exception as e:
            print(f"LLM error: {e}, falling back to regex")
    
    # Fallback to regex
    return simple_parse(user_message)