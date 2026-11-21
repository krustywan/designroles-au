"""Classify every scanned PageUp feed: does it mostly hold Australian jobs? Keep those as daily sources."""
import json, time, sys, concurrent.futures as cf
import connectors as C, tagger as T
import xml.etree.ElementTree as ET
ids = json.load(open("pageup_ids.json"))
def one(x):
    time.sleep(0.4)
    try:
        raw = C.get(f"https://careers.pageuppeople.com/{x['id']}/{x['brand']}/en/rss", timeout=20, tries=2)
        items = list(ET.fromstring(raw).iter("item"))
    except Exception as e:
        return dict(id=x["id"], brand=x["brand"], error=str(e)[:60])
    locs = [it.findtext("job:location", "", C.NS) for it in items]
    au = sum(1 for l in locs if T.AU_RE.search(l or ""))
    desc = " ".join((it.findtext("description") or "")[:300] for it in items[:5])
    return dict(id=x["id"], brand=x["brand"], items=len(items), au=au,
                sample=[(it.findtext("title") or "")[:60] for it in items[:3]], desc=desc[:600])
out = []
with cf.ThreadPoolExecutor(4) as ex:
    for i, r in enumerate(ex.map(one, ids), 1):
        out.append(r)
        if i % 20 == 0:
            print(f"{i}/{len(ids)} done", flush=True)
json.dump(out, open("pageup_au.json", "w"), indent=1)
au = [o for o in out if o.get("items") and o["au"] / o["items"] >= 0.5]
print(len(out), "feeds,", len(au), "mostly Australian,", sum(o["items"] for o in au), "jobs in them,",
      sum(1 for o in out if "error" in o), "errors")
