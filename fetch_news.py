import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import random
from datetime import datetime
from urllib.parse import quote

# We use your exact Google Search URL for the past day on Nairaland
SEARCH_QUERY = "site:nairaland.com"
GOOGLE_URL = f"https://www.google.com/search?q={quote(SEARCH_QUERY)}&tbs=qdr:d"

SEEN_FILE = "seen_urls.json"

# Rotate these to look like different browsers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
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
    # Wait a random time between 2 and 6 seconds before requesting to avoid rate limits
    time.sleep(random.uniform(2, 6))
    
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

    soup = BeautifulSoup(response.text, 'html.parser')
    topics = []

    # Google search results are usually wrapped in an <a> tag containing an <h3> (the title)
    for link in soup.find_all('a', href=True):
        href = link['href']
        title_element = link.find('h3')
        
        # If it has a title and links to nairaland
        if title_element and 'nairaland.com' in href:
            title = title_element.get_text(strip=True)
            
            # --- THE FILTER ---
            # We ONLY want the main frontpage topics. 
            # Frontpage topics look like: https://www.nairaland.com/1234567/topic-name
            # They should NOT have a trailing reply page (like /2, /3) or be a profile, etc.
            
            # This regex ensures the URL ends with a number and a title, with nothing after it
            if re.search(r'nairaland\.com/\d+/[a-z0-9\-]+$', href.lower()):
                # Clean up the URL just in case Google added tracking parameters
                clean_url = href.split('&')[0]
                
                topics.append({
                    'title': title,
                    'link': clean_url,
                    'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
                })

    print(f"Found {len(topics)} valid Nairaland frontpage links on Google.")
    
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
