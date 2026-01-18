#!/usr/bin/env python3
"""
Extract topics from Lex Fridman podcast transcripts and save to CSV.
"""

import os
import re
import csv
from pathlib import Path

TRANSCRIPTS_DIR = Path(__file__).parent.parent / "all_episode_transcripts"
OUTPUT_CSV = Path(__file__).parent / "episode_topics.csv"


def parse_filename(filename: str) -> dict:
    """Extract episode number, guest, and title topics from filename."""
    # Pattern: "452 - Dario Amodei - Anthropic CEO on Claude, AGI & the Future of AI & Humanity.txt"
    match = re.match(r"(\d+)\s*-\s*([^-]+)\s*-\s*(.+)\.txt", filename)
    if match:
        episode_num = match.group(1).strip()
        guest = match.group(2).strip()
        title = match.group(3).strip()
        return {
            "episode_number": episode_num,
            "guest": guest,
            "title": title
        }
    return None


def extract_toc_topics(content: str) -> list[str]:
    """Extract chapter topics from Table of Contents section."""
    topics = []

    # Find the Table of Contents section
    toc_match = re.search(r"## Table of Contents\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not toc_match:
        return topics

    toc_section = toc_match.group(1)

    # Extract chapter names (after timestamp)
    # Pattern matches: "  * 0:00 – Introduction" or "  * 1:05:37 – ASL-3 and ASL-4"
    chapter_pattern = re.findall(r"\*\s*[\d:]+\s*[–-]\s*(.+)", toc_section)

    for chapter in chapter_pattern:
        chapter = chapter.strip()
        # Skip generic chapters
        if chapter.lower() not in ["introduction", "outro", "conclusion"]:
            topics.append(chapter)

    return topics


def extract_title_topics(title: str) -> list[str]:
    """Extract topic keywords from the title."""
    # Split by common delimiters: commas, &, "and", etc.
    # Remove common filler words
    topics = re.split(r",\s*|\s+&\s+|\s+and\s+", title)
    topics = [t.strip() for t in topics if t.strip()]
    return topics


def main():
    episodes = []

    # Get all transcript files
    transcript_files = sorted(TRANSCRIPTS_DIR.glob("*.txt"))

    for filepath in transcript_files:
        filename = filepath.name
        parsed = parse_filename(filename)

        if not parsed:
            print(f"Skipping: {filename}")
            continue

        # Read file content
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        # Extract TOC topics
        toc_topics = extract_toc_topics(content)

        # Extract title topics
        title_topics = extract_title_topics(parsed["title"])

        # Combine and deduplicate topics
        all_topics = title_topics + toc_topics

        episodes.append({
            "episode_number": parsed["episode_number"],
            "guest": parsed["guest"],
            "title": parsed["title"],
            "title_topics": "; ".join(title_topics),
            "chapter_topics": "; ".join(toc_topics),
            "all_topics": "; ".join(all_topics)
        })

    # Sort by episode number
    episodes.sort(key=lambda x: int(x["episode_number"]))

    # Write to CSV
    fieldnames = ["episode_number", "guest", "title", "title_topics", "chapter_topics", "all_topics"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(episodes)

    print(f"Extracted topics from {len(episodes)} episodes")
    print(f"Saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
