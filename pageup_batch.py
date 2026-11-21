"""Find which scanned PageUp feeds hold Australian design/research roles, and name their employers."""
import json, re, time, urllib.request, html
import connectors as C, tagger as T
ids = json.load(open("pageup_ids.json"))
known = {p[0] for p in json.load(open("sources.json"))["pageup"]}
hits = []
for x in ids:
    if x["id"] in known:
        continue
    try:
        jobs = list(C.pageup(x["id"], x["brand"], "?"))
    except Exception as e:
        continue
    keep = [j for j in jobs if T.discipline(j["title"], j["description"]) and T.in_scope_location(j["location"], "", j["description"])]
    if keep:
        hits.append(dict(x, keep=[(j["title"], j["location"]) for j in keep]))
        print(x["id"], x["brand"], x["title"][:50], "|", [(j["title"][:40], j["location"][:25]) for j in keep][:4], flush=True)
    time.sleep(0.4)

def name(x):
    t = html.unescape(x["title"])
    m = re.search(r"(?:Current Opportunities|Jobs at [^-]+|Search & Apply|Careers?|Join Us)\s*[-|:]\s*(.+)$", t)
    if m:
        return m.group(1).strip()
    try:
        req = urllib.request.Request(f"https://careers.pageuppeople.com/{x['id']}/{x['brand']}/en/listing/", headers=C.UA)
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k): return None
        op = urllib.request.build_opener(NoRedirect)
        try:
            r = op.open(req, timeout=15); body = r.read().decode("utf8", "ignore")
            mm = re.search(r'<title>(.*?)</title>', body, re.S)
            return " ".join(html.unescape(mm.group(1)).split()) if mm else ""
        except urllib.error.HTTPError as e:
            return "REDIRECT " + (e.headers.get("Location") or "")
    except Exception as e:
        return ""
for h in hits:
    h["name"] = name(h)
    time.sleep(0.4)
json.dump(hits, open("pageup_hits.json", "w"), indent=1)
for h in hits:
    print(h["id"], h["brand"], "=>", h["name"], "|", len(h["keep"]))
