# utils/youtube_processor.py

from __future__ import annotations

import re
from typing import Dict, List

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(youtube_url: str) -> str:
    """
    Extract YouTube video ID from URL.
    """

    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL")


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds into HH:MM:SS format.
    """

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02}"


def get_youtube_transcript(youtube_url: str) -> List[Dict]:
    """
    Fetch transcript from YouTube video.

    Returns:
        [
            {
                "text": "...",
                "start": 12.4,
                "duration": 4.2,
                "timestamp": "00:00:12",
                "source": youtube_url
            }
        ]
    """

    video_id = extract_video_id(youtube_url)

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    transcript_data = []

    for entry in transcript:
        transcript_data.append(
            {
                "text": entry["text"],
                "start": entry["start"],
                "duration": entry["duration"],
                "timestamp": format_timestamp(entry["start"]),
                "source": youtube_url,
            }
        )

    return transcript_data


def get_full_transcript_text(youtube_url: str) -> str:
    """
    Return full transcript as one combined string.
    """

    transcript_data = get_youtube_transcript(youtube_url)

    return "\n".join(
        f"[{item['timestamp']}] {item['text']}"
        for item in transcript_data
    )