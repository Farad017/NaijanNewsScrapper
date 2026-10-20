import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

URL = "https://www.nairaland.com/"
SEEN_FILE = "seen_urls.json"

def get_seen_urls():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_urls(urls):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(urls), f)

def fetch_frontpage_topics():
    # Using a very realistic browser header to avoid getting blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        print(f"Fetching {URL}...")
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"Successfully fetched! Status code: {response.status_code}")
    except Exception as e:
        print(f"ERROR fetching Nairaland: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    topics = []

    # Find all links on the page
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Nairaland frontpage topics usually look like: /1234567/topic-title
        # We check if it starts with a slash and has a number next
        if href.startswith('/') and len(href) > 2 and href[1].isdigit():
            full_url = "https://www.nairaland.com" + href
            title = link.get_text(strip=True)
            
            # Filter out empty or very short titles
            if title and len(title) > 5:
                topics.append({
                    'title': title,
                    'link': full_url,
                    'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
                })

    print(f"Found {len(topics)} raw links on the page.")
    
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
    new_topics = fetch_frontpage_topics()

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
