#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request
import connectors as C
real=C.candidate; C.candidate=lambda t: True
for name, fn in [("jb", lambda: C.smartrecruiters("JBHi-FiTheGoodGuys1","JB Hi-Fi")), ("racq", lambda: C.taleo("racq.taleo.net","RACQ_External","10100010479","RACQ"))]:
    try: js=list(fn()); print("RES",name,len(js),[j["title"] for j in js if real(j["title"])][:8])
    except Exception as e: print("ERR",name,repr(e)[:200])
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36","Content-Type":"application/json","Accept":"application/json"}
for body in [{"clientNamespace":"sydneywater","jobBoardCode":"candidateportal","cultureCode":"en-AU","paginationStart":0}, {"clientNamespace":"sydneywater","jobBoardCode":"CANDIDATEPORTAL","cultureCode":"en-AU","distanceUnit":0,"paginationStart":0}]:
    try:
        r=urllib.request.urlopen(urllib.request.Request("https://jobs.dayforcehcm.com/api/geo/sydneywater/jobposting/search",data=json.dumps(body).encode(),headers=UA),timeout=30).read().decode()
        print("DF",len(r),r[:700])
    except Exception as e: print("DF ERR",e, getattr(e,"read",lambda:b"")()[:300])
b=urllib.request.urlopen(urllib.request.Request("https://jobs.dayforcehcm.com/en-AU/sydneywater/candidateportal",headers={"User-Agent":UA["User-Agent"]}),timeout=30).read().decode("utf8","ignore")
m=re.search(r'__NEXT_DATA__[^>]*>(.*?)</script>',b,re.S); d=m.group(1) if m else ""
print("DFND",len(d),re.findall(r'"[A-Za-z]*(?:[Tt]itle|[Pp]osting[A-Za-z]*)":',d)[:30]); i=d.find('itle"'); print("DFCTX",d[max(0,i-400):i+500])
for u in ["https://careers.fortescue.com/sitemap.xml","https://careers.fortescue.com/search/?q=designer","https://career10.successfactors.com/career?company=FMGL"]:
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":UA["User-Agent"]}),timeout=30); bb=r.read().decode("utf8","ignore"); print("FMG",u,r.geturl(),len(bb),re.findall(r'href="([^"]*/job/[^"]*)"',bb)[:3],bb[:200].replace("\n"," "))
    except Exception as e: print("FMG",u,"ERR",e)
PY
