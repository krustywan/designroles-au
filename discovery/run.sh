#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request, urllib.parse, html, http.cookiejar
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def req(u,data=None,h=None):
    hh=dict(UA); hh.update(h or {})
    return op.open(urllib.request.Request(u,data=data,headers=hh),timeout=40).read().decode('utf8','ignore')
req("https://jobs.nt.gov.au/Home/Search")
for kw in ["designer","user experience"]:
    d=json.loads(req("https://jobs.nt.gov.au/Home/Search", json.dumps({"Keyword":kw}).encode(), {"Content-Type":"application/json; charset=utf-8"}))
    res=d.get("data") or []; print("NT",kw,len(res),[x["jobTitle"] for x in res][:15])
print("NT keys", list(res[0].keys()) if res else None)
if res: print("NT sample", {k:(str(v)[:80]) for k,v in res[0].items() if k not in ("primaryObjective",)})
b=req("https://jobs.nt.gov.au/Home/Search")
print("NT detail links", sorted(set(re.findall(r'["\']([^"\']*(?:JobDetail|Details|rtfId|ViewJob)[^"\']*)["\']',b+req("https://jobs.nt.gov.au/bundles/HomeSearchTS?v=4ygnzkVQjQXcFjOxcAXKBK_Pm7uQTTDe1vpXQ79j0Sk1"))))[:10])
js=req("https://www.iworkfor.sa.gov.au/js/searchForm.js?1786450965"); print("SAJS", re.sub(r"\s+"," ",js)[:2500])
b=req("https://www.iworkfor.sa.gov.au/")
i=b.find('brsSearchBtn'); print("SABTN", re.sub(r"\s+"," ",b[i-600:i+400]))
PY
