"""
Fetch YouTube transcripts by directly hitting YouTube's internal caption API.
Falls back through multiple methods.
"""

import requests
import re
import json
import os
import xml.etree.ElementTree as ET

VIDEOS = [
    {
        "id": "aircAruvnKk",
        "title": "3Blue1Brown — But what is a Neural Network?",
        "url": "https://www.youtube.com/watch?v=aircAruvnKk"
    },
    {
        "id": "wjZofJX0v4M",
        "title": "3Blue1Brown — Transformers, the tech behind LLMs",
        "url": "https://www.youtube.com/watch?v=wjZofJX0v4M"
    },
    {
        "id": "fHF22Wxuyw4",
        "title": "CampusX — What is Deep Learning? (Hindi)",
        "url": "https://www.youtube.com/watch?v=fHF22Wxuyw4"
    },
    {
        "id": "C6YtPJxNULA",
        "title": "CodeWithHarry — All About ML & Deep Learning (Hindi)",
        "url": "https://www.youtube.com/watch?v=C6YtPJxNULA"
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def get_caption_url(video_id):
    """Extract caption track URL from YouTube video page."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    session = requests.Session()
    resp = session.get(url, headers=HEADERS, timeout=15)
    
    if resp.status_code != 200:
        print(f"  Failed to fetch page: {resp.status_code}")
        return None
    
    # Find captionTracks JSON
    pattern = r'"captionTracks":\s*(\[.*?\])'
    match = re.search(pattern, resp.text)
    
    if not match:
        print("  No captionTracks found in page")
        return None
    
    try:
        tracks = json.loads(match.group(1))
    except json.JSONDecodeError:
        print("  Failed to parse captionTracks JSON")
        return None
    
    print(f"  Found {len(tracks)} caption tracks")
    
    # Prefer English, then Hindi
    for lang_pref in ['en', 'hi', 'en-IN']:
        for track in tracks:
            if track.get('languageCode') == lang_pref:
                base_url = track.get('baseUrl', '')
                if base_url:
                    # Unescape URL
                    base_url = base_url.replace('\\u0026', '&')
                    print(f"  Using {lang_pref} track")
                    return base_url, lang_pref
    
    # Fallback to first available
    if tracks:
        base_url = tracks[0].get('baseUrl', '').replace('\\u0026', '&')
        lang = tracks[0].get('languageCode', 'unknown')
        print(f"  Using fallback track: {lang}")
        return base_url, lang
    
    return None

def fetch_caption_xml(caption_url):
    """Fetch and parse the XML caption track."""
    resp = requests.get(caption_url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        print(f"  Failed to fetch captions: {resp.status_code}")
        return None
    
    try:
        root = ET.fromstring(resp.text)
        entries = []
        for elem in root.findall('.//text'):
            start = float(elem.get('start', 0))
            dur = float(elem.get('dur', 0))
            text = elem.text or ''
            # Clean HTML entities
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            text = text.replace('&#39;', "'").replace('&quot;', '"')
            text = re.sub(r'<[^>]+>', '', text)  # strip HTML tags
            entries.append({
                'text': text.strip(),
                'start': start,
                'duration': dur,
                'timestamp': format_timestamp(start)
            })
        return entries
    except ET.ParseError as e:
        print(f"  XML parse error: {e}")
        return None

def fetch_transcript(video):
    """Fetch transcript for a video."""
    video_id = video['id']
    title = video['title']
    print(f"\nFetching: {title} ({video_id})")
    
    result = get_caption_url(video_id)
    if result is None:
        return None
    
    caption_url, lang = result
    entries = fetch_caption_xml(caption_url)
    
    if entries is None or len(entries) == 0:
        print("  No caption entries found")
        return None
    
    print(f"  SUCCESS: {len(entries)} segments")
    
    return {
        'video_id': video_id,
        'video_title': title,
        'language': lang,
        'segment_count': len(entries),
        'transcript': entries
    }

def main():
    os.makedirs('transcripts', exist_ok=True)
    
    results = {}
    for video in VIDEOS:
        data = fetch_transcript(video)
        if data:
            filename = f"transcripts/{video['id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  Saved to {filename}")
            results[video['id']] = True
        else:
            results[video['id']] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    success = sum(1 for v in results.values() if v)
    print(f"Successfully fetched: {success}/{len(VIDEOS)} transcripts")
    for video in VIDEOS:
        status = "OK" if results.get(video['id']) else "FAIL"
        print(f"  [{status}] {video['title']}")

if __name__ == '__main__':
    main()
