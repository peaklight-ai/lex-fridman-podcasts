#!/usr/bin/env python3
"""
Lex Fridman Podcast Transcript Downloader

Downloads all podcast transcripts and saves them with proper naming:
{episode_number} - {guest_name} - {title}.txt
"""

import requests
from bs4 import BeautifulSoup
import re
import os
import time
from urllib.parse import urljoin
import html2text

BASE_URL = "https://lexfridman.com"
PODCAST_URL = f"{BASE_URL}/podcast"
OUTPUT_DIR = "all_episode_transcripts"

# Be respectful to the server - delay between requests
REQUEST_DELAY = 2  # seconds between requests

# Polite headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) LexFridmanTranscriptArchiver/1.0 (personal research project)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Configure html2text for clean conversion
h2t = html2text.HTML2Text()
h2t.ignore_links = False
h2t.ignore_images = True
h2t.body_width = 0  # No line wrapping


def get_all_episode_urls():
    """Scrape all episode URLs from the main podcast page."""
    print("Fetching main podcast page...")
    response = requests.get(PODCAST_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links that look like episode pages
    episode_urls = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Episode URLs are like /guest-name or https://lexfridman.com/guest-name
        # Exclude known non-episode pages
        exclude_patterns = [
            '/podcast', '/about', '/contact', '/sponsors', '/support',
            '/subscribe', '/youtube', '/twitter', '/instagram', '/linkedin',
            '/patreon', '/paypal', 'mailto:', 'javascript:', '#',
            '/feed', '/rss'
        ]

        if any(pattern in href.lower() for pattern in exclude_patterns):
            continue

        # Strip -transcript suffix if present (some links go directly to transcript)
        if '-transcript' in href:
            href = href.replace('-transcript', '')

        # Check if it's an internal link to an episode
        if href.startswith('/') and len(href) > 1:
            full_url = urljoin(BASE_URL, href)
            episode_urls.add(full_url)
        elif href.startswith(BASE_URL) and href != PODCAST_URL:
            # Make sure it's not just the base URL
            path = href.replace(BASE_URL, '')
            if path and path != '/' and not any(pattern in path.lower() for pattern in exclude_patterns):
                episode_urls.add(href)

    print(f"Found {len(episode_urls)} potential episode URLs")
    return sorted(episode_urls)


def get_episode_info(episode_url):
    """Get episode number and title from an episode page."""
    try:
        response = requests.get(episode_url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for episode number - usually in format "#123" or "Episode 123"
        text = soup.get_text()

        # Try to find episode number from title or heading
        episode_num = None
        title = None
        guest = None

        # Get title from <title> tag (most reliable for episode number)
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            num_match = re.search(r'#(\d+)', title)
            if num_match:
                episode_num = int(num_match.group(1))

        # Fallback to meta tags if no episode number found
        if not episode_num:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                og_content = og_title.get('content', '')
                num_match = re.search(r'#(\d+)', og_content)
                if num_match:
                    episode_num = int(num_match.group(1))
                if not title:
                    title = og_content

        # Extract guest name from URL
        path = episode_url.replace(BASE_URL, '').strip('/')
        guest = path.replace('-', ' ').title()
        # Remove trailing numbers for repeat guests
        guest = re.sub(r'\s+\d+$', '', guest)

        return {
            'episode_num': episode_num,
            'title': title,
            'guest': guest,
            'url': episode_url
        }

    except Exception as e:
        print(f"  Error getting info for {episode_url}: {e}")
        return None


def get_transcript(episode_url):
    """Download the transcript for an episode."""
    # Transcript URL is the episode URL + '-transcript'
    transcript_url = episode_url.rstrip('/') + '-transcript'

    try:
        response = requests.get(transcript_url, headers=HEADERS, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main content area with the transcript
        # Usually in an article or main content div
        content = None

        # Try various selectors for transcript content
        selectors = [
            'article',
            '.entry-content',
            '.post-content',
            '.transcript',
            'main',
            '.content'
        ]

        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                break

        if not content:
            content = soup.body

        if content:
            # Convert HTML to clean text
            transcript_text = h2t.handle(str(content))

            # Clean up the transcript
            transcript_text = clean_transcript(transcript_text)

            return transcript_text

        return None

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise
    except Exception as e:
        print(f"  Error getting transcript from {transcript_url}: {e}")
        return None


def clean_transcript(text):
    """Clean up the transcript text."""
    lines = text.split('\n')
    cleaned_lines = []

    # Skip navigation/header/footer content
    skip_patterns = [
        'skip to content',
        'search for:',
        'subscribe',
        'follow on',
        'support this podcast',
        'sponsors:',
        'copyright',
        'all rights reserved',
        'privacy policy'
    ]

    for line in lines:
        line_lower = line.lower().strip()

        # Skip empty lines at start/end but keep some for formatting
        if not line.strip():
            if cleaned_lines and cleaned_lines[-1].strip():
                cleaned_lines.append('')
            continue

        # Skip navigation/footer content
        if any(pattern in line_lower for pattern in skip_patterns):
            continue

        cleaned_lines.append(line)

    # Join and clean up multiple blank lines
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def sanitize_filename(name):
    """Make a string safe for use as a filename."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')

    # Limit length
    if len(name) > 200:
        name = name[:200]

    return name.strip()


def create_filename(info):
    """Create a proper filename for the transcript."""
    ep_num = info.get('episode_num')
    guest = info.get('guest', 'Unknown')
    title = info.get('title', '')

    # Clean up title - remove "Lex Fridman Podcast", episode number, and guest name duplicates
    if title:
        title = re.sub(r'#\d+\s*[-–—]?\s*', '', title)
        title = re.sub(r'\s*[-–—|]\s*Lex Fridman Podcast.*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^Lex Fridman Podcast\s*[-–—]?\s*', '', title, flags=re.IGNORECASE)
        # Remove guest name from start of title (e.g., "Irving Finkel: Topic" -> "Topic")
        title = re.sub(rf'^{re.escape(guest)}\s*[:–—-]\s*', '', title, flags=re.IGNORECASE)
        # Remove guest name from end of title (e.g., "Topic - Joel David Hamkins" -> "Topic")
        title = re.sub(rf'\s*[-–—]\s*{re.escape(guest)}\s*$', '', title, flags=re.IGNORECASE)
        title = title.strip(' -–—:|')

    if ep_num:
        if title and title.lower() != guest.lower():
            filename = f"{ep_num:03d} - {guest} - {title}"
        else:
            filename = f"{ep_num:03d} - {guest}"
    else:
        if title:
            filename = f"000 - {guest} - {title}"
        else:
            filename = f"000 - {guest}"

    return sanitize_filename(filename) + '.txt'


def main():
    """Main function to download all transcripts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all episode URLs
    episode_urls = get_all_episode_urls()

    if not episode_urls:
        print("No episode URLs found!")
        return

    print(f"\nProcessing {len(episode_urls)} episodes...")

    successful = 0
    failed = 0
    no_transcript = 0

    for i, url in enumerate(episode_urls, 1):
        print(f"\n[{i}/{len(episode_urls)}] Processing: {url}")

        # Get episode info
        info = get_episode_info(url)
        if not info:
            print("  Could not get episode info, skipping...")
            failed += 1
            continue

        print(f"  Episode: #{info.get('episode_num', '?')} - {info.get('guest', 'Unknown')}")

        # Check if we already have this transcript
        filename = create_filename(info)
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            print(f"  Already exists: {filename}")
            successful += 1
            continue

        # Get transcript
        transcript = get_transcript(url)

        if transcript:
            # Save transcript
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {info.get('title', info.get('guest', 'Unknown'))}\n")
                f.write(f"# Episode #{info.get('episode_num', '?')}\n")
                f.write(f"# Source: {url}\n\n")
                f.write(transcript)

            print(f"  Saved: {filename}")
            successful += 1
        else:
            print("  No transcript available")
            no_transcript += 1

        # Be respectful to the server - don't bombard it
        time.sleep(REQUEST_DELAY)

    print(f"\n{'='*50}")
    print(f"DONE!")
    print(f"  Successful: {successful}")
    print(f"  No transcript: {no_transcript}")
    print(f"  Failed: {failed}")
    print(f"  Total files: {len(os.listdir(OUTPUT_DIR))}")


if __name__ == "__main__":
    main()
