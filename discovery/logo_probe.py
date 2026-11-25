"""Probe: find logo candidates for employers with no logo yet. Prints each candidate as a base64 PNG line."""
import re, io, json, base64, urllib.request, urllib.parse, html
from PIL import Image
import cairosvg
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
T = {"cottonon.com": "Cotton On Group"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
def to_png(b, u):
    if b[:5] == b"<?xml" or b"<svg" in b[:2000]:
        b = cairosvg.svg2png(bytestring=b, output_width=512)
    im = Image.open(io.BytesIO(b)); im.load()
    return im.convert("RGBA")
for dom, name in T.items():
    cands = []
    for home in (f"https://www.{dom}/", f"https://web.archive.org/web/2025id_/https://www.{dom}/"):
        try:
            h = get(home).decode("utf8", "ignore"); break
        except Exception as e:
            h = ""; print("ERR", dom, home, e)
    base = home
    for m in re.finditer(r"<img[^>]+>", h, re.I):
        tag = m.group(0)
        if re.search(r"logo|\.svg|brand|header", tag, re.I):
            src = re.search(r'\bsrc="([^"]+)"', tag)
            if src: cands.append(("img", urllib.parse.urljoin(base, html.unescape(src.group(1)))))
    for m in re.finditer(r'<link[^>]+rel="manifest"[^>]+href="([^"]+)"', h):
        try:
            for ic in json.loads(get(urllib.parse.urljoin(base, m.group(1)))).get("icons", []): cands.append(("manifest", urllib.parse.urljoin(base, ic["src"])))
        except Exception as e: print("ERR manifest", e)
    for m in re.finditer(r'url\(([^)]+\.(?:svg|png))\)', h): cands.append(("cssurl", urllib.parse.urljoin(base, m.group(1).strip("'\""))))
    for m in re.finditer(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', h): cands.append(("og", urllib.parse.urljoin(base, m.group(1))))
    for m in re.finditer(r'<link[^>]+rel="[^"]*icon[^"]*"[^>]*>', h, re.I):
        src = re.search(r'href="([^"]+)"', m.group(0))
        if src: cands.append(("icon", urllib.parse.urljoin(base, html.unescape(src.group(1)))))
    # inline svg logos
    for i, m in enumerate(re.finditer(r'<svg[^>]*>.*?</svg>', h, re.S)):
        frag = m.group(0)
        ctx = h[max(0, m.start() - 300):m.start()]
        if len(frag) > 300:
            cands.append(("inline", frag))
        if i > 60: break
    # Wikidata logo (P154) for the organisation
    try:
        q = urllib.parse.urlencode({"action": "wbsearchentities", "search": name, "language": "en", "format": "json", "limit": 3})
        for r in json.loads(get("https://www.wikidata.org/w/api.php?" + q))["search"]:
            ent = json.loads(get(f"https://www.wikidata.org/wiki/Special:EntityData/{r['id']}.json"))["entities"][r["id"]]
            for c in ent.get("claims", {}).get("P154", []):
                fn = c["mainsnak"]["datavalue"]["value"]
                cands.append(("wikidata:" + r["id"], "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(fn.replace(" ", "_")) + "?width=512"))
    except Exception as e:
        print("ERR wikidata", dom, e)
    for kind, u in (("touch", f"https://www.{dom}/apple-touch-icon.png"), ("favsvg", f"https://www.{dom}/favicon.svg"),
                    ("iconhorse", f"https://icon.horse/icon/{dom}"), ("s2", f"https://www.google.com/s2/favicons?domain_url=https://www.{dom}&sz=256")):
        cands.append((kind, u))
    seen = set()
    import os
    os.makedirs(f"discovery/out/{dom}", exist_ok=True)
    n = 0
    for kind, u in cands[:40]:
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
            n += 1
            full.save(f"discovery/out/{dom}/{n:02d}_{re.sub(r'[^a-z0-9]+', '-', kind.lower())[:30]}.png")
            if kind == "inline": open(f"discovery/out/{dom}/{n:02d}_inline.svg", "wb").write(b)
            print(f"CAND\t{dom}\t{n:02d}\t{kind}\t{u[:160] if kind!='inline' else 'inline-svg'}\t{full.size[0]}x{full.size[1]}")
        except Exception as e:
            print("ERR", dom, kind, u[:120], e)
