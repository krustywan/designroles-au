"""Download a logo for each employer in employer_domains.json into logos/.

Run on GitHub's computers before build_board.py. Tries the employer's own
large icon first (apple-touch-icon), then public favicon services, then the
icons listed on the employer's home page, keeping the sharpest one found.
Logos are only used to identify the employer next to their job ads."""
import json, os, re, struct, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "DesignRolesAU-bot/0.1 (+https://github.com/krustywan/designroles-au)"
OUT = "logos"
# Sites whose large icon isn't their logo (e.g. a photo); use their favicon instead.
SKIP_TOUCH = {"acer.org", "flightcentre.com.au"}
# Sites whose small icons are not their logo either; go straight to Wikidata.
SKIP_ICONS = {"acer.org"}


def kind_and_size(b):
    """Return (file extension, smallest side in pixels) for PNG, JPEG, ICO or SVG data."""
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24]); return "png", min(w, h)
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF: i += 1; continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", b[i + 5:i + 9]); return "jpg", min(w, h)
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
        return "jpg", 0
    if b[:4] == b"\x00\x00\x01\x00":
        n = struct.unpack("<H", b[4:6])[0]
        best = max(((b[6 + 16 * k] or 256) for k in range(min(n, 20)) if 6 + 16 * k < len(b)), default=0)
        return "ico", best
    if b"<svg" in b[:3000]:
        return "svg", 999
    return "", 0


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()


def page_icons(domain):
    """Icon links declared on the employer's home page, biggest first."""
    for home in (f"https://www.{domain}/", f"https://{domain}/"):
        try:
            page = fetch(home).decode("utf8", "ignore")[:300000]
        except Exception:
            continue
        found = []
        for tag in re.findall(r"<link[^>]+>", page, re.I):
            rel = re.search(r'rel=["\']([^"\']+)', tag, re.I)
            href = re.search(r'href=["\']([^"\']+)', tag, re.I)
            if not rel or not href or "icon" not in rel.group(1).lower():
                continue
            sz = re.search(r'sizes=["\'](\d+)', tag, re.I)
            found.append((int(sz.group(1)) if sz else (999 if href.group(1).endswith(".svg") else 0), urllib.parse.urljoin(home, href.group(1))))
        return [u for _, u in sorted(found, reverse=True)][:4]
    return []


def wikidata_logo(name, domain):
    """The logo Wikidata lists for this organisation (property P154), if its official website matches."""
    api = "https://www.wikidata.org/w/api.php?format=json&"
    try:
        hits = json.loads(fetch(api + urllib.parse.urlencode({"action": "wbsearchentities", "search": re.sub(r"\s*\(.*?\)", "", name), "language": "en", "limit": 5})))["search"]
        for h in hits:
            ent = json.loads(fetch(api + urllib.parse.urlencode({"action": "wbgetentities", "ids": h["id"], "props": "claims"})))["entities"][h["id"]]["claims"]
            sites = [c["mainsnak"].get("datavalue", {}).get("value", "") for c in ent.get("P856", [])]
            logos = [c["mainsnak"].get("datavalue", {}).get("value", "") for c in ent.get("P154", [])]
            if logos and any(domain in str(u) for u in sites):
                return ["https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(logos[0]) + "?width=256"]
    except Exception:
        pass
    return []


def one(item):
    name, domain = item
    if domain in SKIP_ICONS:
        urls = []
    else:
        urls = [] if domain in SKIP_TOUCH else [f"https://{domain}/apple-touch-icon.png", f"https://www.{domain}/apple-touch-icon.png"]
        urls += [f"https://www.google.com/s2/favicons?domain={domain}&sz=128", f"https://www.google.com/s2/favicons?domain_url=https://www.{domain}/&sz=256",
                 f"https://icons.duckduckgo.com/ip3/{domain}.ico", f"https://unavatar.io/{domain}?fallback=false"]
    best = (0, "", b"")
    for stage in (urls, "page", "wikidata"):
        if stage == "page" and domain in SKIP_ICONS:
            continue
        for url in stage if isinstance(stage, list) else page_icons(domain) if stage == "page" else wikidata_logo(name, domain):
            try:
                b = fetch(url)
            except Exception:
                continue
            ext, px = kind_and_size(b)
            if ext and px > best[0]:
                best = (px, ext, b)
            if best[0] >= 64:
                break
        if best[0] >= 64:
            break
    if best[0] >= 32:  # anything smaller looks blurry, so the board shows initials instead
        open(os.path.join(OUT, f"{domain}.{best[1]}"), "wb").write(best[2])
    return domain, best[0] if best[0] >= 32 else 0


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = {}
    for k, v in json.load(open("employer_domains.json")).items():
        if not k.startswith("_"):
            names.setdefault(v, k)
    domains = sorted((n, d) for d, n in names.items())
    with ThreadPoolExecutor(8) as ex:
        got = list(ex.map(one, domains))
    print(f"logos: {sum(1 for _, w in got if w)} of {len(got)} found;", "missing:", [d for d, w in got if not w])
