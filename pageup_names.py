import json, re, html, time, urllib.request, urllib.error, concurrent.futures as cf
import connectors as C
au = [o for o in json.load(open("pageup_au.json")) if o.get("items") and o["au"] / o["items"] >= 0.5]
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NR)
def name(o):
    time.sleep(0.3)
    u = f"https://careers.pageuppeople.com/{o['id']}/{o['brand']}/en/listing/"
    try:
        r = op.open(urllib.request.Request(u, headers=C.UA), timeout=15)
        b = r.read().decode("utf8", "ignore")
        m = re.search(r"<title>(.*?)</title>", b, re.S)
        return o["id"], "title", " ".join(html.unescape(m.group(1)).split()) if m else ""
    except urllib.error.HTTPError as e:
        return o["id"], "redirect", e.headers.get("Location", "")
    except Exception as e:
        return o["id"], "error", str(e)[:40]
with cf.ThreadPoolExecutor(4) as ex:
    res = list(ex.map(name, au))
d = {o["id"]: o for o in au}
for i, kind, val in res:
    o = d[i]
    print(f"{i}|{o['brand']}|{o['items']}|{kind}|{val[:70]}|{' / '.join(o['sample'])[:90]}")
