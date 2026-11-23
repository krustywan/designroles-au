"""Probe: find logo candidates for employers with no logo yet. Prints each candidate as a base64 PNG line."""
import re, io, json, base64, urllib.request, urllib.parse, html
from PIL import Image
import cairosvg
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
T = {"naa.gov.au": "National Archives of Australia", "wesfarmers.com.au": "Wesfarmers", "epa.vic.gov.au": "Environment Protection Authority Victoria",
     "dffh.vic.gov.au": "Department of Families, Fairness and Housing", "transport.vic.gov.au": "Department of Transport and Planning Victoria",
     "vic.gov.au": "Victorian Government"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read()
def to_png(b, u):
    if b[:5] == b"<?xml" or b"<svg" in b[:2000]:
        b = cairosvg.svg2png(bytestring=b, output_width=512)
    im = Image.open(io.BytesIO(b)); im.load()
    return im.convert("RGBA")
for dom, name in T.items():
    cands = []
    for home in (f"https://www.{dom}/", f"https://{dom}/"):
        try:
            h = get(home).decode("utf8", "ignore"); break
        except Exception as e:
            h = ""; print("ERR", dom, home, e)
    base = home
    for m in re.finditer(r"<img[^>]+>", h, re.I):
        tag = m.group(0)
        if re.search(r"logo", tag, re.I):
            src = re.search(r'\bsrc="([^"]+)"', tag)
            if src: cands.append(("img", urllib.parse.urljoin(base, html.unescape(src.group(1)))))
    for m in re.finditer(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', h): cands.append(("og", urllib.parse.urljoin(base, m.group(1))))
    for m in re.finditer(r'<link[^>]+rel="[^"]*icon[^"]*"[^>]*>', h, re.I):
        src = re.search(r'href="([^"]+)"', m.group(0))
        if src: cands.append(("icon", urllib.parse.urljoin(base, html.unescape(src.group(1)))))
    # inline svg logos
    for i, m in enumerate(re.finditer(r'<svg[^>]*>.*?</svg>', h, re.S)):
        frag = m.group(0)
        ctx = h[max(0, m.start() - 300):m.start()]
        if re.search(r"logo|brand|home", ctx + frag[:300], re.I) and len(frag) > 400:
            cands.append(("inline", frag))
        if i > 60: break
    # Wikimedia Commons
    try:
        q = urllib.parse.urlencode({"action": "query", "list": "search", "srsearch": f"{name} logo", "srnamespace": 6, "format": "json", "srlimit": 4})
        for r in json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))["query"]["search"]:
            q2 = urllib.parse.urlencode({"action": "query", "titles": r["title"], "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 512, "format": "json"})
            for p in json.loads(get("https://commons.wikimedia.org/w/api.php?" + q2))["query"]["pages"].values():
                ii = p.get("imageinfo", [{}])[0]
                if ii.get("thumburl"): cands.append(("commons:" + r["title"], ii["thumburl"]))
    except Exception as e:
        print("ERR commons", dom, e)
    seen = set()
    for kind, u in cands[:14]:
        key = u[:300]
        if key in seen: continue
        seen.add(key)
        try:
            b = u.encode() if kind == "inline" else get(u)
            im = to_png(b, u)
            im.thumbnail((256, 256))
            out = io.BytesIO(); im.save(out, "PNG")
            # full-resolution copy too, for the chosen one
            full = to_png(b, u); full.thumbnail((512, 512)); fo = io.BytesIO(); full.save(fo, "PNG")
            print(f"CAND\t{dom}\t{kind}\t{u[:160] if kind!='inline' else 'inline-svg'}\t{im.size[0]}x{im.size[1]}\t{base64.b64encode(out.getvalue()).decode()}\t{base64.b64encode(fo.getvalue()).decode()}")
        except Exception as e:
            print("ERR", dom, kind, u[:120], e)
