import feedparser
import xml.etree.ElementTree as ET
import os
from datetime import datetime

SRC = "https://www.kalerkantho.com/rss.xml"
PRINT_PATHS = ["daily_kalerkantho_part1.xml", "daily_kalerkantho_part2.xml"]

def filter_print_entries(entries):
    """Return entries matching /print-edition/ only."""
    result = []
    for e in entries:
        link = getattr(e, "link", None) or getattr(e, "id", None)
        if not link:
            continue
        link = link.strip()
        if "/print-edition/" in link:
            result.append(e)
    return result

def add_items_print(entries, paths):
    """Add new print entries to two XML files in chunks of 100, avoiding duplicates."""
    # Collect existing links from all existing print XMLs
    existing_links = set()
    for path in paths:
        if os.path.exists(path):
            root = ET.parse(path).getroot()
            channel = root.find("channel")
            existing_links.update({i.findtext("link") for i in channel.findall("item")})

    # Sort newest first
    entries_sorted = sorted(entries, key=lambda e: getattr(e, "published_parsed", datetime.utcnow()), reverse=True)

    # Remove duplicates
    new_entries = []
    for entry in entries_sorted:
        link = getattr(entry, "link", None) or getattr(entry, "id", None)
        if not link:
            continue
        link = link.strip()
        if link in existing_links:
            continue
        existing_links.add(link)
        new_entries.append(entry)

    # Split into chunks of 100 items
    chunks = [new_entries[i:i+100] for i in range(0, len(new_entries), 100)]

    # Write each chunk to its respective XML file
    for i, chunk in enumerate(chunks):
        path = paths[i] if i < len(paths) else f"daily_kalerkantho_part{i+1}.xml"
        rss_root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss_root, "channel")
        for entry in chunk:
            link = getattr(entry, "link", None) or getattr(entry, "id", None)
            if not link:
                continue
            link = link.strip()
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = entry.title
            ET.SubElement(item, "link").text = link
            ET.SubElement(item, "pubDate").text = getattr(entry, "published", datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
            ET.SubElement(item, "guid", isPermaLink="false").text = link
        ET.ElementTree(rss_root).write(path, encoding="utf-8", xml_declaration=True)
        print(f"{path} written with {len(chunk)} items")

# Parse the feed
feed = feedparser.parse(SRC)
print(f"Total entries in feed: {len(feed.entries)}")

# Filter /print-edition/ entries
print_entries = filter_print_entries(feed.entries)
print(f"Print entries matched: {len(print_entries)}")

# Add to XMLs
add_items_print(print_entries, PRINT_PATHS)