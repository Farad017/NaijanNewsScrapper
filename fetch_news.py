import requests
from bs4 import BeautifulSoup
import json
import os
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching Nairaland: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    topics = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/') and len(href) > 2 and href[1].isdigit():
            full_url = "https://www.nairaland.com" + href
            title = link.get_text(strip=True)
            if title and len(title) > 5:
                topics.append({
                    'title': title,
                    'link': full_url,
                    'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
                })

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

    print(f"Found {len(fresh_topics)} new topics.")

if __name__ == "__main__":
    main()
