#!/usr/bin/env bash
python3 - <<'PY'
import re, urllib.request, html
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
get=lambda u: urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read().decode('utf8','ignore')
b=get("https://www.iworkfor.sa.gov.au/")
t=re.sub(r"<script.*?</script>|<style.*?</style>"," ",b,flags=re.S)
print("SA rows", len(re.findall(r'Advert\[ID\]',b)), "jobref", len(re.findall(r'pageID=\d+[^"]*Advert',b)))
for m in re.findall(r'href="([^"]*(?:Advert|advert|job|Job)[^"]*)"',b)[:15]: print("SA HREF", html.unescape(m)[:200])
i=b.find('orderByCol'); print("SA AROUND", re.sub(r"\s+"," ",b[i-200:i+3500])[:3700])
txt=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",t)); j=txt.find('Closing'); print("SA TEXT", txt[max(0,j-1500):j+1500])
js=get("https://jobs.nt.gov.au/bundles/HomeSearchTS?v=4ygnzkVQjQXcFjOxcAXKBK_Pm7uQTTDe1vpXQ79j0Sk1")
print("NT JS len", len(js))
for m in sorted(set(re.findall(r'["\'](/[A-Za-z]+/[A-Za-z]+[^"\']{0,60})["\']',js)))[:40]: print("NT URL", m)
for m in re.findall(r'.{0,200}(?:ajax|fetch|\$\.(?:get|post)|url\s*:).{0,250}',js)[:12]: print("NT CALL", m[:450])
PY
