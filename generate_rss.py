import json
import os
from datetime import datetime
from xml.sax.saxutils import escape

NEWS_FILE = "news.json"
FEED_FILE = "feed.xml"
MAX_ITEMS = 100

FEED_TITLE = "Nairaland Frontpage"
FEED_LINK = "https://www.nairaland.com/"
FEED_DESC = "Latest topics from the Nairaland frontpage"

def load_history():
    """Load previously included items so the feed stays populated between runs."""
    if os.path.exists(FEED_FILE):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(FEED_FILE)
            root = tree.getroot()
            items = []
            for item in root.findall('./channel/item'):
                items.append({
                    'title': item.findtext('title', ''),
                    'link': item.findtext('link', ''),
                    'pubDate': item.findtext('pubDate', ''),
                })
            return items
        except Exception as e:
            print(f"Could not parse existing feed: {e}")
            return []
    return []

def main():
    # Start with what's already in the feed
    history = load_history()

    # Load the newest items found by fetch_news.py
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, 'r') as f:
            fresh = json.load(f)
    else:
        fresh = []

    # Put fresh items at the top
    combined = fresh + history

    # Remove duplicates by link, keep first occurrence
    seen = set()
    items = []
    for i in combined:
        if i['link'] and i['link'] not in seen:
            items.append(i)
            seen.add(i['link'])

    # Trim to MAX_ITEMS
    items = items[:MAX_ITEMS]

    now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

    # Build the XML
    xml_parts = []
    xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_parts.append('<rss version="2.0">')
    xml_parts.append('<channel>')
    xml_parts.append(f'<title>{escape(FEED_TITLE)}</title>')
    xml_parts.append(f'<link>{escape(FEED_LINK)}</link>')
    xml_parts.append(f'<description>{escape(FEED_DESC)}</description>')
    xml_parts.append(f'<lastBuildDate>{now}</lastBuildDate>')

    for item in items:
        xml_parts.append('<item>')
        xml_parts.append(f'<title>{escape(item["title"])}</title>')
        xml_parts.append(f'<link>{escape(item["link"])}</link>')
        xml_parts.append(f'<guid isPermaLink="true">{escape(item["link"])}</guid>')
        if item.get('pubDate'):
            xml_parts.append(f'<pubDate>{escape(item["pubDate"])}</pubDate>')
        xml_parts.append('</item>')

    xml_parts.append('</channel>')
    xml_parts.append('</rss>')

    with open(FEED_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_parts))

    print(f"Wrote {len(items)} items to {FEED_FILE}")

if __name__ == "__main__":
    main()
