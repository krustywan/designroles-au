"""Download a logo for each employer in employer_domains.json into logos/.

Run on GitHub's computers before build_board.py. Tries the employer's own
large icon first (apple-touch-icon), then Google's public favicon service.
Logos are only used to identify the employer next to their job ads."""
import json, os, struct, urllib.request
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


def one(domain):
    for url in (f"https://{domain}/apple-touch-icon.png", f"https://www.{domain}/apple-touch-icon.png",
                f"https://www.google.com/s2/favicons?domain={domain}&sz=128"):
        try:
            b = fetch(url)
        except Exception:
            continue
        w, h = size(b)
        if min(w, h) >= 48:
            open(os.path.join(OUT, domain + ".png"), "wb").write(b)
            return domain, w
    return domain, 0


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    domains = sorted({v for k, v in json.load(open("employer_domains.json")).items() if not k.startswith("_")})
    with ThreadPoolExecutor(8) as ex:
        got = list(ex.map(one, domains))
    print(f"logos: {sum(1 for _, w in got if w)} of {len(got)} found;", "missing:", [d for d, w in got if not w])
