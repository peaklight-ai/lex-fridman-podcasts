#!/usr/bin/env python3
"""
Download ALL Lex Fridman transcripts using Selenium to get playlist URLs
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import time
import re
import pickle
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "all_episode_transcripts"
OUTPUT_DIR.mkdir(exist_ok=True)
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLrAXtmErZgOdP_8GztsuKi9nrraNbKKp4"

text_formatter = TextFormatter()


def get_existing_episodes():
    """Get episode numbers we already have"""
    existing = set()
    for f in OUTPUT_DIR.glob("*.txt"):
        match = re.match(r'^(\d+)', f.name)
        if match:
            existing.add(int(match.group(1)))
    return existing


def find_all(a_str, sub):
    """Find all occurrences of substring"""
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)


def scrape_playlist():
    """Use Selenium to get all video URLs and titles from playlist"""
    print("Opening Chrome to scrape playlist...")

    options = Options()
    options.add_argument("--headless")  # Run without GUI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(PLAYLIST_URL)
    time.sleep(3)

    # Scroll to load all videos
    print("Scrolling to load all videos...")
    last_height = 0
    for i in range(30):  # More scrolls to get all ~490 videos
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight)')
        time.sleep(1.5)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        if (i + 1) % 10 == 0:
            print(f"  Scrolled {i+1} times...")

    html = driver.page_source
    driver.quit()

    # Extract URLs
    url_marker = 'href="/watch?v='
    urls = []
    for pos in find_all(html, url_marker):
        video_id = html[pos+15:pos+26]
        if '&' in video_id:
            video_id = video_id.split('&')[0]
        if len(video_id) == 11 and video_id not in [u['id'] for u in urls]:
            urls.append({'id': video_id, 'url': f'https://www.youtube.com/watch?v={video_id}'})

    # Extract titles - find them near the URLs
    title_marker = 'video-title'
    videos = []

    for pos in find_all(html, title_marker):
        # Look for title text
        chunk = html[pos:pos+500]
        title_match = re.search(r'title="([^"]+)"', chunk)
        if title_match:
            title = title_match.group(1)
            # Find associated video ID
            id_match = re.search(r'/watch\?v=([a-zA-Z0-9_-]{11})', chunk)
            if id_match:
                vid_id = id_match.group(1)
                if not any(v['id'] == vid_id for v in videos):
                    videos.append({'id': vid_id, 'title': title})

    print(f"Found {len(videos)} videos from playlist")
    return videos


def extract_episode_number(title):
    """Extract episode number from title"""
    match = re.search(r'#(\d+)', title)
    return int(match.group(1)) if match else None


def sanitize_filename(title):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')
    return re.sub(r'\s+', ' ', title).strip()[:120]


def download_transcript(video_id, title, episode_num):
    """Download transcript for a video"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = text_formatter.format_transcript(transcript)

        # Clean title
        clean = re.sub(r'\s*\|\s*Lex Fridman Podcast.*$', '', title)
        clean = re.sub(r'^#\d+\s*[–-]\s*', '', clean)
        parts = re.split(r'\s*[:\-–]\s*', clean, maxsplit=1)
        guest = parts[0].strip() if parts else "Unknown"
        topic = parts[1].strip() if len(parts) > 1 else clean

        safe_title = sanitize_filename(f"{guest} - {topic}")

        if episode_num:
            filename = f"{episode_num} - {safe_title}.txt"
        else:
            filename = f"video_{video_id} - {safe_title}.txt"

        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n")
            if episode_num:
                f.write(f"# Episode #{episode_num}\n")
            f.write(f"# Source: https://www.youtube.com/watch?v={video_id}\n\n")
            f.write(text)

        return True
    except Exception as e:
        return False


def main():
    print("=" * 60)
    print("LEX FRIDMAN TRANSCRIPT DOWNLOADER (PLAYLIST)")
    print("=" * 60)

    existing = get_existing_episodes()
    print(f"Already have: {len(existing)} episodes\n")

    # Scrape playlist
    videos = scrape_playlist()

    # Filter to episodes we don't have
    to_download = []
    for v in videos:
        ep_num = extract_episode_number(v['title'])
        if ep_num and ep_num not in existing:
            v['episode_num'] = ep_num
            to_download.append(v)
        elif not ep_num:
            v['episode_num'] = None
            # Skip non-numbered videos for now

    to_download.sort(key=lambda x: x.get('episode_num') or 9999)

    print(f"\nNeed to download: {len(to_download)} episodes")
    print()

    success = 0
    failed = 0

    for v in to_download:
        ep = v.get('episode_num', '?')
        title = v['title'][:50]

        if download_transcript(v['id'], v['title'], v.get('episode_num')):
            print(f"✓ #{ep}: {title}")
            success += 1
        else:
            print(f"✗ #{ep}: No transcript")
            failed += 1

        time.sleep(1)

    print()
    print("=" * 60)
    print(f"Downloaded: {success}")
    print(f"No transcript: {failed}")
    print(f"Total now: {len(existing) + success}")
    print("=" * 60)


if __name__ == "__main__":
    main()
