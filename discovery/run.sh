#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request, urllib.parse, html, http.cookiejar
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def req(u,data=None,h=None):
    hh=dict(UA); hh.update(h or {})
    return op.open(urllib.request.Request(u,data=data,headers=hh),timeout=40).read().decode('utf8','ignore')
req("https://jobs.nt.gov.au/Home/Search")
d=json.loads(req("https://jobs.nt.gov.au/Home/Search", json.dumps({"Keyword":"design"}).encode(), {"Content-Type":"application/json; charset=utf-8"}))
r0=d["data"][0]; print("NTKEYS", {k:str(v)[:60] for k,v in r0.items() if k!="primaryObjective"})
print("NTT", [x["jobTitle"] for x in d["data"]])
b=req("https://www.iworkfor.sa.gov.au/")
for m in re.finditer(r'<(INPUT|BUTTON)([^>]*(?:searchButton|resetButton)[^>]*)>',b,re.I): print("SABTN", m.group(0)[:300])
form=re.search(r'<FORM name="mainForm".*?</FORM>',b,re.S|re.I).group(0)
fields=[]
for m in re.finditer(r'<INPUT([^>]*)>',form,re.I):
    a=m.group(1); n=re.search(r'name="([^"]+)"',a); v=re.search(r'value=[\'"]([^\'"]*)[\'"]',a); t=re.search(r'type="([^"]+)"',a)
    if n and (not t or t.group(1).lower() not in ("checkbox","button","reset")): fields.append((n.group(1), v.group(1) if v else ""))
fields=[(k,("designer" if k=="Advert[Data]" else ("Search" if k=="action" else v))) for k,v in fields]
r=req("https://www.iworkfor.sa.gov.au/page.php?pageID=842&windowUID=0", urllib.parse.urlencode(fields).encode(), {"Content-Type":"application/x-www-form-urlencoded","Referer":"https://www.iworkfor.sa.gov.au/"})
print("SA len", len(r), "results?", re.findall(r'(\d+)\s*(?:jobs?|results?) found',r,re.I)[:3])
for m in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]{4,120}?)\s*</a>',r):
    if re.search(r'design|research|ux|content|service',m[1],re.I): print("SA A", html.unescape(m[0])[:200], "|", m[1])
i=r.find('id="report"'); body=re.sub(r"<script.*?</script>|<style.*?</style>"," ",r[i:],flags=re.S); print("SATEXT", re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",body))[:3000])
print("SALINKS", [html.unescape(x)[:160] for x in re.findall(r'href="([^"]+)"',r[i:]) if 'jb/' in x or 'Advert' in x][:15])
k=0; #print("SACTX", re.sub(r"\s+"," ",re.sub(r"<script.*?</script>","",r[r.find('id="report"')-200:r.find('id="report"')+2500],flags=re.S))[:2500])
PY
