import requests, xml.etree.ElementTree as ET, os

SRC = "https://www.kalerkantho.com/rss.xml"
FILES = {
    "opinion": "opinion.xml",
    "world": "world.xml"
}

def load_existing(path):
    if not os.path.exists(path):
        root = ET.Element("rss"); channel = ET.SubElement(root, "channel")
        return root
    return ET.parse(path).getroot()

def add_items(root, items):
    channel = root.find("channel")
    existing_links = {i.findtext("link") for i in channel.findall("item")}
    for itm in items:
        link = itm.findtext("link")
        if link not in existing_links:
            channel.append(itm)

    # max 500
    all_items = channel.findall("item")
    for extra in all_items[:-500]:
        channel.remove(extra)

def filter_items(src_items, key):
    out = []
    for item in src_items:
        link = item.findtext("link") or ""
        if f"/{key}/" in link:
            out.append(item)
    return out

def save(root, path):
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

r = requests.get(SRC, timeout=30)
src_root = ET.fromstring(r.content)
src_items = src_root.find("channel").findall("item")

for key, path in FILES.items():
    root = load_existing(path)
    items = filter_items(src_items, key)
    add_items(root, items)
    save(root, path)