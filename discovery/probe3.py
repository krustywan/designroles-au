"""Guess Workday tenants and ATS board names for companies we couldn't map from their websites."""
import json, re, sys, urllib.request, urllib.error, concurrent.futures as cf, time
UA = {"User-Agent": "Mozilla/5.0 (compatible; DesignRolesAU/0.1)"}
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NR)
def head(u):
    try:
        r = op.open(urllib.request.Request(u, headers=UA), timeout=12); return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "")
    except Exception as e:
        return type(e).__name__, ""
def getj(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=12) as r: return json.loads(r.read())
    except Exception: return None
GUESSES = json.load(open(sys.argv[1]))
def one(item):
    name, toks = item
    hits = []
    for t in toks:
        for wd in ("wd3", "wd105", "wd5", "wd1", "wd103"):
            s, loc = head(f"https://{t}.{wd}.myworkdayjobs.com/")
            if s in (301, 302, 303, 307, 308) and loc and (f"{t}.{wd}" in loc or loc.startswith("/")) and "maintenance" not in loc:
                hits.append(f"workday {t}.{wd} -> {loc}")
                break
            time.sleep(0.2)
        d = getj(f"https://boards-api.greenhouse.io/v1/boards/{t}/jobs")
        if d and d.get("jobs") is not None: hits.append(f"greenhouse {t} {len(d['jobs'])}")
        d = getj(f"https://api.lever.co/v0/postings/{t}?mode=json&limit=1")
        if isinstance(d, list) and d: hits.append(f"lever {t}")
        d = getj(f"https://api.ashbyhq.com/posting-api/job-board/{t}")
        if d and d.get("jobs"): hits.append(f"ashby {t} {len(d['jobs'])}")
        d = getj(f"https://api.smartrecruiters.com/v1/companies/{t}/postings?country=au&limit=1")
        if d and d.get("totalFound"): hits.append(f"smartrecruiters {t} {d['totalFound']}")
    return name, hits
with cf.ThreadPoolExecutor(6) as ex:
    for name, hits in ex.map(one, GUESSES.items()):
        print("GUESS", name, "|", "; ".join(hits) or "-", flush=True)
