#!/usr/bin/env python3
"""
Lex Fridman Podcast Episode Downloader
Downloads actual video/audio files from YouTube

Requirements:
    pip install yt-dlp scrapetube

Usage:
    python download_episodes.py              # Download as audio (MP3) - smaller files
    python download_episodes.py --video      # Download as video (MP4)
    python download_episodes.py --start 400  # Start from episode 400+
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
import re
import time

try:
    import scrapetube
except ImportError:
    print("Installing scrapetube...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scrapetube"])
    import scrapetube

# Configuration
CHANNEL_ID = "UCSHZKyawb77ixDdsGog4iWA"  # Lex Fridman's YouTube channel
OUTPUT_DIR = Path("episodes")
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_episode_number(title):
    """Extract episode number from title (e.g., '#123' or 'Lex Fridman Podcast #123')"""
    match = re.search(r'#(\d+)', title)
    if match:
        return int(match.group(1))
    return None


def sanitize_filename(title):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')
    title = re.sub(r'\s+', ' ', title)
    return title.strip()[:100]


def episode_exists(episode_num, output_dir):
    """Check if episode already downloaded"""
    pattern = f"{episode_num:03d}_*"
    matches = list(output_dir.glob(pattern + ".*"))
    return len(matches) > 0


def download_episode(video_id, title, episode_num, audio_only=True):
    """Download a single episode using yt-dlp"""

    safe_title = sanitize_filename(title)

    if episode_num:
        output_template = str(OUTPUT_DIR / f"{episode_num:03d}_{safe_title}.%(ext)s")
    else:
        output_template = str(OUTPUT_DIR / f"{safe_title}.%(ext)s")

    url = f"https://www.youtube.com/watch?v={video_id}"

    if audio_only:
        # Download best audio, convert to MP3
        cmd = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",  # Best quality
            "-o", output_template,
            "--no-playlist",
            "--no-warnings",
            url
        ]
    else:
        # Download best video+audio as MP4
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_template,
            "--no-playlist",
            "--no-warnings",
            url
        ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
        if result.returncode == 0:
            return True
        else:
            print(f"  Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  Timeout downloading episode")
        return False
    except Exception as e:
        print(f"  Exception: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download Lex Fridman Podcast episodes")
    parser.add_argument("--video", action="store_true", help="Download video (MP4) instead of audio (MP3)")
    parser.add_argument("--start", type=int, default=0, help="Start from episode number N")
    parser.add_argument("--end", type=int, default=9999, help="End at episode number N")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of downloads (0 = unlimited)")
    args = parser.parse_args()

    audio_only = not args.video
    mode = "AUDIO (MP3)" if audio_only else "VIDEO (MP4)"

    print("=" * 60)
    print("LEX FRIDMAN PODCAST EPISODE DOWNLOADER")
    print("=" * 60)
    print(f"Mode: {mode}")
    print(f"Output: {OUTPUT_DIR.absolute()}")
    if args.start > 0:
        print(f"Starting from episode: #{args.start}")
    if args.end < 9999:
        print(f"Ending at episode: #{args.end}")
    print()

    # Check if yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: yt-dlp not found!")
        print("Install it with: pip install yt-dlp")
        print("Or on Mac: brew install yt-dlp")
        sys.exit(1)

    # Fetch video list
    print("Fetching video list from channel...")
    videos = list(scrapetube.get_channel(CHANNEL_ID, sort_by="oldest"))

    # Parse videos and filter to podcast episodes
    episodes = []
    for video in videos:
        try:
            video_id = video.get('videoId')
            title = video.get('title', {}).get('runs', [{}])[0].get('text', '')

            if not video_id or not title:
                continue

            episode_num = extract_episode_number(title)

            # Filter: Only numbered podcast episodes in range
            if episode_num and args.start <= episode_num <= args.end:
                episodes.append({
                    'video_id': video_id,
                    'title': title,
                    'episode_num': episode_num
                })
        except Exception:
            continue

    # Sort by episode number
    episodes.sort(key=lambda x: x['episode_num'])

    print(f"Found {len(episodes)} podcast episodes in range")
    print()

    # Download episodes
    success = 0
    skipped = 0
    failed = 0
    downloaded = 0

    for ep in episodes:
        video_id = ep['video_id']
        title = ep['title']
        episode_num = ep['episode_num']

        # Check if already downloaded
        if episode_exists(episode_num, OUTPUT_DIR):
            print(f"⊘ #{episode_num}: Already exists, skipping")
            skipped += 1
            continue

        # Check download limit
        if args.limit > 0 and downloaded >= args.limit:
            print(f"\nReached download limit of {args.limit}")
            break

        print(f"⬇ #{episode_num}: {title[:50]}...")

        if download_episode(video_id, title, episode_num, audio_only):
            print(f"  ✓ Downloaded successfully")
            success += 1
            downloaded += 1
        else:
            print(f"  ✗ Failed")
            failed += 1

        # Small delay between downloads
        time.sleep(2)

    # Summary
    print()
    print("=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Downloaded: {success}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Failed: {failed}")
    print(f"Output folder: {OUTPUT_DIR.absolute()}")

    # Estimate storage
    if audio_only:
        est_size = success * 150  # ~150 MB per episode MP3 (3hr podcast)
    else:
        est_size = success * 2000  # ~2 GB per episode MP4

    print(f"Estimated storage used: ~{est_size / 1000:.1f} GB")


if __name__ == "__main__":
    main()
