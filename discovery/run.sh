#!/usr/bin/env bash
python3 - <<'PY'
import re, json, traceback
import connectors as C
real = C.candidate
C.candidate = lambda t: True   # count everything, then show which would be kept
tests = [
 ("tyro", lambda: C.teamtailor("careers.tyro.com", "Tyro")),
 ("racq", lambda: C.taleo("racq.taleo.net", "RACQ_External", "10100010479", "RACQ")),
 ("sydneywater", lambda: C.dayforce("sydneywater", "Sydney Water")),
 ("mecca", lambda: C.workday("mecca.wd3.myworkdayjobs.com", "mecca", "careers", "Mecca")),
 ("fortescue", lambda: C.sf_rss("careers.fortescue.com", "Fortescue", "en_US")),
 ("abc-cw", lambda: C.pageup(516, "cw", "ABC")),
 ("abc-caw", lambda: C.pageup(516, "caw", "ABC")),
]
for name, fn in tests:
    try:
        js = list(fn()); keep = [j for j in js if real(j["title"])]
        print("RES", name, "all", len(js), "kept", len(keep), "| sample", [j["title"] for j in js[:4]], "| kept", [j["title"] for j in keep][:8])
        if js: print("ONE", name, json.dumps({k: (str(v)[:90]) for k, v in js[0].items()}))
    except Exception as e:
        print("ERR", name, repr(e)[:300])
import urllib.request
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36","Accept":"text/html,application/xhtml+xml","Accept-Language":"en-AU,en;q=0.9"}
b = urllib.request.urlopen(urllib.request.Request("https://www.jbhifi.com.au/pages/jobs", headers=UA), timeout=30).read().decode("utf8","ignore")
print("JB", re.findall(r'(?:company|companyIdentifier|company_code)["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]+)', b)[:5], re.findall(r'smartrecruiters\.com/[A-Za-z0-9_-]+', b)[:5])
for u in ["https://ecu.nga.net.au/cp/index.cfm?audiencetypecode=ext", "https://ecu.nga.net.au/?jati=", "https://ecu.nga.net.au/"]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30); bb = r.read().decode("utf8","ignore")
        print("NGA", u, r.status, r.geturl(), len(bb), re.findall(r'href="([^"]*(?:jati|jobs)[^"]*)"', bb)[:8])
    except Exception as e: print("NGA", u, "ERR", e, getattr(e, "headers", {}).get("Server") if hasattr(e, "headers") else "")
PY
