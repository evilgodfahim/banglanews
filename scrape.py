import feedparser, xml.etree.ElementTree as ET, os
from datetime import datetime

SRC = "https://www.kalerkantho.com/rss.xml"
FILES = {
    "opinion": "opinion.xml",
    "world": "world.xml"
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
        if entry.link in existing_links:
            continue
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = entry.title
        ET.SubElement(item, "link").text = entry.link
        ET.SubElement(item, "pubDate").text = entry.published if hasattr(entry, "published") else datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(item, "guid", isPermaLink="false").text = entry.link

    # Keep max 500
    all_items = channel.findall("item")
    for extra in all_items[:-500]:
        channel.remove(extra)

def filter_entries(entries, key):
    return [e for e in entries if f"/{key}/" in e.link]

# Parse feed safely
feed = feedparser.parse(SRC)

for key, path in FILES.items():
    root = load_existing(path)
    filtered = filter_entries(feed.entries, key)
    add_items(root, filtered)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)