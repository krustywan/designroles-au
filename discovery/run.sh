#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request, urllib.parse, html, http.cookiejar
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def req(u,data=None,h=None):
    hh=dict(UA); hh.update(h or {})
    return op.open(urllib.request.Request(u,data=data,headers=hh),timeout=40).read().decode('utf8','ignore')
# NT
try:
    req("https://jobs.nt.gov.au/Home/Search")
    r=req("https://jobs.nt.gov.au/Home/Search", json.dumps({"Keyword":"design"}).encode(), {"Content-Type":"application/json; charset=utf-8","X-Requested-With":"XMLHttpRequest"})
    d=json.loads(r); print("NT keys", list(d.keys())); res=d.get("data") or []
    print("NT n", len(res)); print("NT first", json.dumps(res[0])[:1500] if res else r[:500])
except Exception as e: print("NT ERR", e)
# SA
b=req("https://www.iworkfor.sa.gov.au/")
form=re.search(r'<FORM name="mainForm".*?</FORM>',b,re.S|re.I).group(0)
fields={}
for m in re.finditer(r'<INPUT([^>]*)>',form,re.I):
    a=m.group(1); n=re.search(r'name="([^"]+)"',a); v=re.search(r'value=[\'"]([^\'"]*)[\'"]',a)
    if n: fields[n.group(1)]=v.group(1) if v else ""
print("SA fields", {k:v[:30] for k,v in fields.items()})
print("SA text inputs", re.findall(r'<INPUT[^>]*type="text"[^>]*>',form,re.I)[:6])
print("SA buttons", re.findall(r'<(?:INPUT|BUTTON)[^>]*(?:submit|searchButton)[^>]*>',form,re.I)[:4])
fields["t_67[-1]"]="designer"; fields["action"]=fields.get("action") or "search"
r=req("https://www.iworkfor.sa.gov.au/page.php?pageID=842&windowUID=0", urllib.parse.urlencode(fields).encode(), {"Content-Type":"application/x-www-form-urlencoded"})
print("SA result len", len(r))
for m in re.findall(r'href="([^"]*Advert[^"]*)"[^>]*>([^<]{3,100})<',r)[:20]: print("SA JOB", html.unescape(m[0])[:200], "|", m[1].strip())
k=r.find('esign'); print("SA ctx", re.sub(r"\s+"," ",r[max(0,k-1500):k+800]))
PY
