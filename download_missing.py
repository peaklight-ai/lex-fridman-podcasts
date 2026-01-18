#!/usr/bin/env python3
"""
Download missing Lex Fridman transcripts for episodes 276-489
"""

import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import time
from pathlib import Path
import re

OUTPUT_DIR = Path(__file__).parent / "all_episode_transcripts"
CHANNEL_ID = "UCSHZKyawb77ixDdsGog4iWA"

# Episodes we're missing
MISSING = [277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,386,478]

text_formatter = TextFormatter()


def sanitize_filename(title):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')
    return re.sub(r'\s+', ' ', title).strip()[:150]


def extract_episode_number(title):
    match = re.search(r'#(\d+)', title)
    return int(match.group(1)) if match else None


def download_transcript(video_id, title, episode_num):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text_content = text_formatter.format_transcript(transcript)

        # Clean title
        clean_title = re.sub(r'\s*\|\s*Lex Fridman Podcast\s*', '', title)
        clean_title = re.sub(r'^#\d+\s*[–-]\s*', '', clean_title)
        parts = re.split(r'\s*[:\-–]\s*', clean_title, maxsplit=1)
        guest_name = parts[0].strip() if parts else "Unknown"
        topic = parts[1].strip() if len(parts) > 1 else clean_title

        safe_title = sanitize_filename(f"{guest_name} - {topic}")
        filename = f"{episode_num} - {safe_title}.txt"
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n")
            f.write(f"# Episode #{episode_num}\n")
            f.write(f"\n# Transcript\n\n")
            f.write(text_content)

        return True, guest_name
    except Exception as e:
        return False, str(e)[:50]


def main():
    print("=" * 60)
    print("DOWNLOADING MISSING TRANSCRIPTS")
    print(f"Missing: {len(MISSING)} episodes")
    print("=" * 60)
    print()

    # Fetch all videos
    print("Fetching video list from YouTube...")
    videos = list(scrapetube.get_channel(CHANNEL_ID, sort_by="oldest"))

    # Build episode -> video map
    episode_map = {}
    for video in videos:
        try:
            video_id = video.get('videoId')
            title = video.get('title', {}).get('runs', [{}])[0].get('text', '')
            ep_num = extract_episode_number(title)
            if ep_num and video_id:
                episode_map[ep_num] = {'video_id': video_id, 'title': title}
        except:
            continue

    print(f"Found {len(episode_map)} episodes with numbers")
    print()

    success = 0
    failed = 0
    not_found = 0

    for ep_num in sorted(MISSING):
        if ep_num not in episode_map:
            print(f"⚠ #{ep_num}: Not found on channel")
            not_found += 1
            continue

        video = episode_map[ep_num]
        ok, info = download_transcript(video['video_id'], video['title'], ep_num)

        if ok:
            print(f"✓ #{ep_num}: {info[:40]}")
            success += 1
        else:
            print(f"✗ #{ep_num}: {info}")
            failed += 1

        time.sleep(1)

    print()
    print("=" * 60)
    print(f"Downloaded: {success}")
    print(f"No transcript: {failed}")
    print(f"Not on channel: {not_found}")
    print("=" * 60)


if __name__ == "__main__":
    main()
