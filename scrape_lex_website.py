#!/usr/bin/env python3
"""
Scrape transcripts directly from lexfridman.com
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "all_episode_transcripts"
OUTPUT_DIR.mkdir(exist_ok=True)

BASE_URL = "https://lexfridman.com/podcast/"


def get_existing_episodes():
    """Get list of episode numbers we already have"""
    existing = set()
    for f in OUTPUT_DIR.glob("*.txt"):
        match = re.match(r'^(\d+)', f.name)
        if match:
            existing.add(int(match.group(1)))
    return existing


def get_episode_list():
    """Get all episode URLs from the podcast page"""
    print("Fetching episode list from lexfridman.com...")

    resp = requests.get(BASE_URL, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')

    episodes = []

    # Find all episode links
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        # Match patterns like /episode-name/ or lexfridman.com/episode-name
        if 'lexfridman.com/' in href or (href.startswith('/') and not href.startswith('//')):
            # Skip non-episode pages
            skip = ['podcast', 'about', 'contact', 'sponsor', 'newsletter', 'youtube', 'twitter', 'instagram']
            if any(s in href.lower() for s in skip):
                continue

            # Get full URL
            if href.startswith('/'):
                url = f"https://lexfridman.com{href}"
            else:
                url = href

            if 'lexfridman.com/' in url and url not in [e['url'] for e in episodes]:
                episodes.append({'url': url})

    return episodes


def get_transcript(url):
    """Fetch transcript from episode page"""
    try:
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Try to find episode number
        title_tag = soup.find('title')
        title = title_tag.text if title_tag else ""

        ep_match = re.search(r'#(\d+)', title)
        episode_num = int(ep_match.group(1)) if ep_match else None

        # Find transcript section
        transcript_div = soup.find('div', class_='transcript') or \
                        soup.find('div', id='transcript') or \
                        soup.find(id='transcript-container')

        if not transcript_div:
            # Try finding by text content
            for div in soup.find_all('div'):
                text = div.get_text()
                if len(text) > 5000 and ('Lex Fridman' in text or 'podcast' in text.lower()):
                    transcript_div = div
                    break

        if transcript_div:
            transcript = transcript_div.get_text(separator='\n', strip=True)
            return episode_num, title, transcript

        return episode_num, title, None

    except Exception as e:
        return None, None, None


def sanitize_filename(title):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '')
    return re.sub(r'\s+', ' ', title).strip()[:120]


def main():
    print("=" * 60)
    print("LEXFRIDMAN.COM TRANSCRIPT SCRAPER")
    print("=" * 60)

    existing = get_existing_episodes()
    print(f"Already have: {len(existing)} episodes")

    # Get episode URLs by checking sequential episode pages
    print("\nChecking episodes 1-500 on lexfridman.com...")

    success = 0
    failed = 0
    skipped = 0

    for ep_num in range(1, 500):
        if ep_num in existing:
            continue

        # Try common URL patterns
        urls_to_try = [
            f"https://lexfridman.com/{ep_num}/",
            f"https://lexfridman.com/episode-{ep_num}/",
        ]

        found = False
        for url in urls_to_try:
            try:
                resp = requests.get(url, timeout=10, allow_redirects=True)
                if resp.status_code == 200 and 'transcript' in resp.text.lower():
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    # Get title
                    title_tag = soup.find('title')
                    title = title_tag.text if title_tag else f"Episode {ep_num}"
                    title = title.replace(' - Lex Fridman Podcast', '').replace(' | Lex Fridman', '').strip()

                    # Find transcript
                    transcript_text = None

                    # Look for transcript section
                    for selector in ['#transcript', '.transcript', '[class*="transcript"]']:
                        el = soup.select_one(selector)
                        if el:
                            transcript_text = el.get_text(separator='\n', strip=True)
                            break

                    if not transcript_text:
                        # Try to find main content with timestamps
                        main = soup.find('main') or soup.find('article') or soup.find('div', class_='entry-content')
                        if main:
                            text = main.get_text()
                            if re.search(r'\(\d+:\d+:\d+\)', text) or re.search(r'\[\d+:\d+\]', text):
                                transcript_text = main.get_text(separator='\n', strip=True)

                    if transcript_text and len(transcript_text) > 1000:
                        # Save it
                        safe_title = sanitize_filename(title)
                        filename = f"{ep_num} - {safe_title}.txt"
                        filepath = OUTPUT_DIR / filename

                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(f"# {title}\n")
                            f.write(f"# Episode #{ep_num}\n")
                            f.write(f"# Source: {url}\n\n")
                            f.write(transcript_text)

                        print(f"✓ #{ep_num}: {title[:50]}")
                        success += 1
                        found = True
                        break

            except Exception as e:
                pass

        if not found:
            # Only report if it's in a range we expect to have
            if ep_num >= 1 and ep_num <= 489:
                failed += 1

        time.sleep(0.5)  # Be nice to the server

        # Progress update
        if ep_num % 50 == 0:
            print(f"... checked up to #{ep_num}")

    print()
    print("=" * 60)
    print(f"New downloads: {success}")
    print(f"Not found/no transcript: {failed}")
    print(f"Total now: {len(existing) + success}")
    print("=" * 60)


if __name__ == "__main__":
    main()
