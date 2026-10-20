import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import random
from datetime import datetime

# We switch from Google to Bing
SEARCH_QUERY = "site:nairaland.com"
BING_URL = f"https://www.bing.com/search?q={SEARCH_QUERY}&filters=ex1%3a%22ez1%22" # ez1 = Past 24 hours

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

def fetch_from_bing():
    time.sleep(random.uniform(1, 3))
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        print(f"Fetching from Bing: {BING_URL}")
        response = requests.get(BING_URL, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"Successfully fetched Bing! Status code: {response.status_code}")
    except Exception as e:
        print(f"ERROR fetching Bing: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    topics = []

    # Bing uses <li class="b_algo"> for search results
    for result in soup.find_all('li', class_='b_algo'):
        link_element = result.find('a', href=True)
        if not link_element:
            continue
            
        href = link_element['href']
        title = link_element.get_text(strip=True)
        
        # Filter for frontpage topics only (ends with number/title, no /2 replies)
        if 'nairaland.com' in href and re.search(r'nairaland\.com/\d+/[a-z0-9\-]+$', href.lower()):
            # Clean URL just in case
            clean_url = href.split('?')[0]
            
            topics.append({
                'title': title,
                'link': clean_url,
                'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            })

    print(f"Found {len(topics)} valid Nairaland frontpage links on Bing.")
    
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
    new_topics = fetch_from_bing()

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
