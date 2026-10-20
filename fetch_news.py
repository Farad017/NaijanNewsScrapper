import requests
import json
import os
import re
import time
import random
from datetime import datetime
from urllib.parse import quote

SEARCH_QUERY = "site:nairaland.com"
GOOGLE_URL = f"https://www.google.com/search?q={quote(SEARCH_QUERY)}&tbs=qdr:d&num=50"
SEEN_FILE = "seen_urls.json"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

def get_seen_urls():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_urls(urls):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(urls), f)

def fetch_from_google():
    # Wait to avoid rate limits
    time.sleep(random.uniform(2, 5))
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        print(f"Fetching from Google: {GOOGLE_URL}")
        response = requests.get(GOOGLE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"Successfully fetched Google! Status code: {response.status_code}")
    except Exception as e:
        print(f"ERROR fetching Google: {e}")
        return []

    html_content = response.text
    topics = []

    # This regex searches the raw HTML for any Nairaland frontpage link
    # It looks for nairaland.com/ followed by numbers, a slash, and a title (e.g., nairaland.com/1234567/some-topic)
    pattern = r'(https?://[a-zA-Z0-9\.]*nairaland\.com/\d+/[a-z0-9\-]+)(?:&|"|\'|<|\s|$)'
    
    matches = re.findall(pattern, html_content, re.IGNORECASE)
    
    print(f"Found {len(matches)} potential Nairaland links in raw HTML.")

    for url in matches:
        # Clean up the URL (remove any Google tracking at the end)
        clean_url = url.split('&')[0].strip()
        
        # Sometimes Google wraps the URLs, let's make sure it's a direct link
        if not clean_url.startswith("http"):
            continue
            
        # Extract a basic title from the URL for now
        # (e.g., https://www.nairaland.com/1234567/some-topic becomes "Some Topic")
        url_parts = clean_url.split('/')
        if len(url_parts) >= 5:
            raw_title = url_parts[-1] # gets "some-topic"
            title = raw_title.replace('-', ' ').title()
        else:
            title = "Nairaland Topic"

        topics.append({
            'title': title,
            'link': clean_url,
            'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
        })

    # Remove duplicates within this batch
    unique_topics = []
    seen_in_batch = set()
    for t in topics:
        if t['link'] not in seen_in_batch:
            unique_topics.append(t)
            seen_in_batch.add(t['link'])

    return unique_topics

def main():
    seen_urls = get_seen_urls()
    new_topics = fetch_from_google()

    fresh_topics = []
    for topic in new_topics:
        if topic['link'] not in seen_urls:
            fresh_topics.append(topic)
            seen_urls.add(topic['link'])

    save_seen_urls(seen_urls)

    with open('news.json', 'w') as f:
        json.dump(fresh_topics, f, indent=2)

    print(f"Saved {len(fresh_topics)} new topics to news.json.")

if __name__ == "__main__":
    main()
