"""Download a logo for each employer in employer_domains.json into logos/.

Run on GitHub's computers before build_board.py. Tries the employer's own
large icon first (apple-touch-icon), then Google's public favicon service.
Logos are only used to identify the employer next to their job ads."""
import json, os, re, struct, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "DesignRolesAU-bot/0.1 (+https://github.com/krustywan/designroles-au)"
OUT = "logos"


def size(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    return (0, 0)  # not a PNG; skip it to keep things simple


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()


# Sites whose large icon isn't their logo (e.g. a photo); use their favicon instead.
SKIP_TOUCH = {"acer.org", "flightcentre.com.au"}


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
        return [u for _, u in sorted(found, reverse=True)]
    return []


def one(domain):
    urls = [] if domain in SKIP_TOUCH else [f"https://{domain}/apple-touch-icon.png", f"https://www.{domain}/apple-touch-icon.png"]
    urls += [f"https://www.google.com/s2/favicons?domain={domain}&sz=128"]
    tried_page = False
    while urls:
        url = urls.pop(0)
        try:
            b = fetch(url)
        except Exception:
            b = b""
        if b[:600].lstrip().startswith((b"<svg", b"<?xml")) and b"<svg" in b[:2000]:
            open(os.path.join(OUT, domain + ".svg"), "wb").write(b)
            return domain, 999
        w, h = size(b) if b else (0, 0)
        if min(w, h) >= 48:
            open(os.path.join(OUT, domain + ".png"), "wb").write(b)
            return domain, w
        if not urls and not tried_page:
            tried_page = True
            urls = page_icons(domain)[:4]
    return domain, 0


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    domains = sorted({v for k, v in json.load(open("employer_domains.json")).items() if not k.startswith("_")})
    with ThreadPoolExecutor(8) as ex:
        got = list(ex.map(one, domains))
    print(f"logos: {sum(1 for _, w in got if w)} of {len(got)} found;", "missing:", [d for d, w in got if not w])
