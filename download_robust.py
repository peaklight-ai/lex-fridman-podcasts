#!/usr/bin/env python3
"""
Robust transcript downloader - tries multiple methods to get YouTube transcripts.
The youtube_transcript_api often fails to find transcripts that DO exist (proven by tactiq.io).
This script tries multiple approaches for each video.
"""

import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import json
import os
import time
from pathlib import Path
import re

CHANNEL_ID = "UCSHZKyawb77ixDdsGog4iWA"
OUTPUT_DIR = Path(__file__).parent / "all_episode_transcripts"
VIDEO_IDS_CACHE = Path(__file__).parent / "video_ids_cache.json"
DELAY_SECONDS = 0.5

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
text_formatter = TextFormatter()


def sanitize_filename(title):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')
    title = re.sub(r'\s+', ' ', title)
    return title.strip()[:150]


def extract_episode_number(title):
    match = re.search(r'#(\d+)', title)
    if match:
        return int(match.group(1))
    return None


def file_exists(episode_num):
    if episode_num:
        files = list(OUTPUT_DIR.glob(f"{episode_num:03d} - *.txt"))
        return len(files) > 0
    return False


def get_transcript_robust(video_id):
    """Try multiple methods to get transcript"""

    # Method 1: List available transcripts and try each one
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try manual transcripts first (highest quality)
        try:
            for transcript in transcript_list:
                if not transcript.is_generated:
                    return transcript.fetch()
        except:
            pass

        # Try auto-generated in English
        try:
            transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
            return transcript.fetch()
        except:
            pass

        # Try any available transcript
        try:
            for transcript in transcript_list:
                return transcript.fetch()
        except:
            pass

    except Exception as e:
        pass

    # Method 2: Direct API call (default behavior)
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except:
        pass

    # Method 3: Try with explicit language codes
    for lang in ['en', 'en-US', 'en-GB', 'a.en']:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        except:
            pass

    return None


def download_transcript(video_id, title, episode_titles_json):
    """Download transcript for a single video"""

    episode_num = extract_episode_number(title)

    if episode_num and file_exists(episode_num):
        return "exists"

    transcript = get_transcript_robust(video_id)

    if not transcript:
        return "failed"

    # Format transcript
    text_content = text_formatter.format_transcript(transcript)

    # Extract guest and topic from title
    clean_title = re.sub(r'\s*\|\s*Lex Fridman Podcast\s*', '', title)
    clean_title = re.sub(r'^#\d+\s*[–-]\s*', '', clean_title)
    parts = re.split(r'\s*[:\-–]\s*', clean_title, maxsplit=1)
    guest_name = parts[0].strip() if parts else "Unknown"
    topic = parts[1].strip() if len(parts) > 1 else clean_title

    safe_title = sanitize_filename(f"{guest_name} - {topic}")

    if episode_num:
        filename = f"{episode_num:03d} - {safe_title}.txt"
    else:
        filename = f"video_{video_id} - {safe_title}.txt"

    filepath = OUTPUT_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n")
        if episode_num:
            f.write(f"# Episode #{episode_num}\n")
        f.write(f"# Video ID: {video_id}\n")
        f.write(f"\n")
        f.write(text_content)

    return "downloaded"


def main():
    print("=" * 60)
    print("ROBUST TRANSCRIPT DOWNLOADER")
    print("=" * 60)

    # Load or fetch video list
    if VIDEO_IDS_CACHE.exists():
        print("Loading cached video list...")
        with open(VIDEO_IDS_CACHE, 'r') as f:
            episodes = json.load(f)
    else:
        print("Fetching video list from YouTube...")
        videos = list(scrapetube.get_channel(CHANNEL_ID, sort_by="oldest"))

        episodes = []
        for video in videos:
            try:
                video_id = video.get('videoId')
                title = video.get('title', {}).get('runs', [{}])[0].get('text', '')

                if video_id and title:
                    episode_num = extract_episode_number(title)
                    if episode_num:
                        episodes.append({
                            'video_id': video_id,
                            'title': title,
                            'episode_num': episode_num
                        })
            except:
                continue

        episodes.sort(key=lambda x: x['episode_num'])

        with open(VIDEO_IDS_CACHE, 'w') as f:
            json.dump(episodes, f, indent=2)

    print(f"Found {len(episodes)} podcast episodes")

    # Load episode titles for better naming
    episode_titles_path = Path(__file__).parent / "episode_titles.json"
    episode_titles = {}
    if episode_titles_path.exists():
        with open(episode_titles_path, 'r') as f:
            episode_titles = json.load(f)

    downloaded = 0
    existed = 0
    failed = 0
    failed_episodes = []

    for idx, ep in enumerate(episodes, 1):
        result = download_transcript(ep['video_id'], ep['title'], episode_titles)

        if result == "downloaded":
            print(f"✓ #{ep['episode_num']:03d}")
            downloaded += 1
        elif result == "exists":
            existed += 1
        else:
            print(f"✗ #{ep['episode_num']:03d}: No transcript")
            failed += 1
            failed_episodes.append(ep['episode_num'])

        if idx % 50 == 0:
            print(f"\n--- {idx}/{len(episodes)} | New: {downloaded} | Failed: {failed} ---\n")

        time.sleep(DELAY_SECONDS)

    print()
    print("=" * 60)
    print(f"Downloaded: {downloaded}")
    print(f"Already existed: {existed}")
    print(f"Failed: {failed}")
    print("=" * 60)

    if failed_episodes:
        with open(Path(__file__).parent / "still_missing.json", 'w') as f:
            json.dump(failed_episodes, f)
        print(f"Missing episodes saved to still_missing.json")


if __name__ == "__main__":
    main()
