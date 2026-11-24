#!/usr/bin/env bash
python3 - <<'PY'
import re, urllib.request, html
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40); return r.status,r.geturl(),r.read().decode('utf8','ignore')
    except Exception as e: return str(e)[:100],u,''
for u in ["https://www.iworkfor.sa.gov.au/","https://www.iworkfor.sa.gov.au/jobs?keywords=designer","https://www.iworkfor.sa.gov.au/search?keywords=designer",
          "https://jobs.nt.gov.au/Home/Search","https://jobs.nt.gov.au/Home/Search?Keywords=designer"]:
    st,fu,b=get(u); print("URL",st,fu,len(b))
    links=sorted(set(h for h in re.findall(r'(?:href|action|src)="([^"]+)"',b) if re.search(r'job|search|api|vacanc|position',h,re.I)))
    print("LINKS", [html.unescape(x)[:120] for x in links[:40]])
    print("FORMS", re.findall(r'<form[^>]*>',b,re.I)[:4])
    print("INPUTS", re.findall(r'<input[^>]*name="([^"]+)"',b,re.I)[:20])
    print("APIS", sorted(set(re.findall(r'["\'](/[^"\']*(?:api|Api|search|Search)[^"\']*)["\']',b)))[:20])
PY
