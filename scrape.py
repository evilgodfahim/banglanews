import feedparser
import xml.etree.ElementTree as ET
import os
from datetime import datetime

SRC = "https://www.kalerkantho.com/rss.xml"
FILES = {
    "opinion": "opinion.xml",
    "world": "world.xml",
    "print": "daily_kalerkantho.xml"
}

def load_existing(path):
    if not os.path.exists(path):
        root = ET.Element("rss", version="2.0")
        ET.SubElement(root, "channel")
        return root
    return ET.parse(path).getroot()

def add_items(root, items):
    channel = root.find("channel")
    existing_links = {i.findtext("link") for i in channel.findall("item")}
    
    for entry in items:
        # Get link from entry.link or entry.id/guid
        link = getattr(entry, "link", None) or getattr(entry, "id", None)
        if not link or link in existing_links:
            continue

        item = ET.Element("item")
        ET.SubElement(item, "title").text = entry.title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "pubDate").text = getattr(entry, "published", datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        ET.SubElement(item, "guid", isPermaLink="false").text = link
        
        # Insert at the top
        channel.insert(0, item)

    # Keep max 500 items
    all_items = channel.findall("item")
    for extra in all_items[:-500]:
        channel.remove(extra)

def filter_entries(entries, key):
    result = []
    for e in entries:
        link = getattr(e, "link", None) or getattr(e, "id", None)
        if not link:
            continue
        link = link.strip()
        if key == "opinion" and any(x in link for x in ["/opinion/", "/editorial/", "/sub-editorial/"]):
            result.append(e)
        elif key == "world" and ("/world/" in link or "/deshe-deshe/" in link):
            result.append(e)
        elif key == "print" and "/print-edition/" in link:
            result.append(e)
    return result

# Parse feed safely
feed = feedparser.parse(SRC)
print(f"Total entries in feed: {len(feed.entries)}")  # debug

for key, path in FILES.items():
    root = load_existing(path)
    filtered = filter_entries(feed.entries, key)
    print(f"{key}: {len(filtered)} entries matched")  # debug
    add_items(root, filtered)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    print(f"{path} written successfully")