import requests
import json
import os
import re
import time
import random
import xml.etree.ElementTree as ET
from datetime import datetime

# We use r.jina.ai to bypass Nairaland's firewall and get its native RSS feed
PROXY_URL = "https://r.jina.ai/https://www.nairaland.com/feed"
SEEN_FILE = "seen_urls.json"

def get_seen_urls():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_urls(urls):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(urls), f)

def fetch_topics():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        print(f"Fetching from proxy: {PROXY_URL}")
        response = requests.get(PROXY_URL, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"Successfully fetched proxy! Status code: {response.status_code}")
    except Exception as e:
        print(f"ERROR fetching proxy: {e}")
        return []

    topics = []
    
    # Parse the XML data
    try:
        # We look for the RSS items in the text
        root = ET.fromstring(response.text)
        for item in root.findall('./channel/item'):
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            pub_date = item.findtext('pubDate', datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000'))
            
            if title and link:
                topics.append({
                    'title': title,
                    'link': link,
                    'pubDate': pub_date
                })
    except Exception as e:
        print(f"Error parsing XML: {e}")
        print("The proxy might have returned a non-XML page. Here is the first 200 characters:")
        print(response.text[:200])
        return []

    print(f"Found {len(topics)} links from the Nairaland feed.")
    
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
    new_topics = fetch_topics()

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
