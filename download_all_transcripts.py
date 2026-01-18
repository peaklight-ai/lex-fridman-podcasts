#!/usr/bin/env python3
"""
Lex Fridman Podcast Transcript Downloader
Downloads all transcripts from Lex Fridman's YouTube channel

Requirements: pip install scrapetube youtube-transcript-api
"""

import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import json
import os
import time
from pathlib import Path
import re

# Configuration
CHANNEL_ID = "UCSHZKyawb77ixDdsGog4iWA"  # Lex Fridman's YouTube channel
OUTPUT_DIR = Path(__file__).parent / "all_episode_transcripts"
DELAY_SECONDS = 1

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

text_formatter = TextFormatter()


def sanitize_filename(title):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')
    title = re.sub(r'\s+', ' ', title)
    return title.strip()[:150]


def extract_episode_number(title):
    """Extract episode number from title"""
    match = re.search(r'#(\d+)', title)
    if match:
        return int(match.group(1))
    return None


def file_exists(episode_num):
    """Check if transcript already downloaded by episode number"""
    if episode_num:
        files = list(OUTPUT_DIR.glob(f"{episode_num} - *.txt"))
        return len(files) > 0
    return False


def download_transcript(video_id, title, index_number):
    """Download transcript for a single video"""

    episode_num = extract_episode_number(title)

    # Skip if already downloaded
    if file_exists(episode_num):
        print(f"⊘ Skipping #{episode_num}: Already exists")
        return True

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Format transcript text
        text_content = text_formatter.format_transcript(transcript)

        # Clean up title for filename
        # Remove "| Lex Fridman Podcast" suffix
        clean_title = re.sub(r'\s*\|\s*Lex Fridman Podcast\s*', '', title)
        # Remove episode number prefix like "#452 – "
        clean_title = re.sub(r'^#\d+\s*[–-]\s*', '', clean_title)
        # Extract guest name (usually before the first colon or dash in what remains)
        parts = re.split(r'\s*[:\-–]\s*', clean_title, maxsplit=1)
        guest_name = parts[0].strip() if parts else "Unknown"
        topic = parts[1].strip() if len(parts) > 1 else clean_title

        safe_title = sanitize_filename(f"{guest_name} - {topic}")

        if episode_num:
            filename = f"{episode_num} - {safe_title}.txt"
        else:
            filename = f"video_{index_number:03d} - {safe_title}.txt"

        filepath = OUTPUT_DIR / filename

        # Write transcript with header
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n")
            f.write(f"# Episode #{episode_num}\n" if episode_num else "")
            f.write(f"# Source: https://lexfridman.com/{guest_name.lower().replace(' ', '-')}\n")
            f.write(f"\n# Transcript for {title}\n\n")
            f.write(text_content)

        print(f"✓ #{episode_num}: {guest_name[:40]}")
        return True

    except Exception as e:
        error_msg = str(e)
        if "TranscriptsDisabled" in error_msg or "NoTranscriptFound" in error_msg:
            print(f"⚠ #{episode_num}: No transcript available")
        else:
            print(f"✗ #{episode_num}: Error - {error_msg[:50]}")
        return False


def main():
    print("=" * 60)
    print("LEX FRIDMAN TRANSCRIPT DOWNLOADER")
    print("=" * 60)
    print(f"Output: {OUTPUT_DIR}")
    print()

    print("Fetching video list...")
    videos = list(scrapetube.get_channel(CHANNEL_ID, sort_by="oldest"))

    # Parse and filter to podcast episodes only
    episodes = []
    for video in videos:
        try:
            video_id = video.get('videoId')
            title = video.get('title', {}).get('runs', [{}])[0].get('text', '')

            if not video_id or not title:
                continue

            episode_num = extract_episode_number(title)

            # Only include numbered episodes (actual podcast episodes)
            if episode_num:
                episodes.append({
                    'video_id': video_id,
                    'title': title,
                    'episode_num': episode_num
                })
        except:
            continue

    # Sort by episode number
    episodes.sort(key=lambda x: x['episode_num'])

    print(f"Found {len(episodes)} podcast episodes")
    print()

    success = 0
    skipped = 0
    failed = 0

    for idx, ep in enumerate(episodes, 1):
        result = download_transcript(ep['video_id'], ep['title'], idx)

        if result:
            if file_exists(ep['episode_num']):
                skipped += 1
            else:
                success += 1
        else:
            failed += 1

        # Progress every 50
        if idx % 50 == 0:
            print(f"\n--- {idx}/{len(episodes)} processed ---\n")

        time.sleep(DELAY_SECONDS)

    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"New downloads: {success}")
    print(f"Already existed: {skipped}")
    print(f"Failed/unavailable: {failed}")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
