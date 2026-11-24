python3 - <<'PY'
import re, urllib.request, html
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40); return r.status,r.read().decode('utf8','ignore')
    except Exception as e: return str(e)[:100],''
st,b=get("https://jobs.careers.vic.gov.au/jobtools/jncustomsearch.viewFullSingle?in_organid=14160&in_jnCounter=226728009&in_jobDate=All&in_searchbox=YES&in_summary=S")
for h in sorted(set(re.findall(r'(?:href|action)="([^"]+)"',b))): 
    if 'jncustom' in h or 'search' in h.lower(): print("LINK", html.unescape(h)[:200])
for u in ["https://jobs.careers.vic.gov.au/jobtools/jncustomsearch.jobsearch?in_organid=14160",
          "https://jobs.careers.vic.gov.au/jobtools/jncustomsearch.searchResults?in_organid=14160&in_jobDate=All",
          "https://jobs.careers.vic.gov.au/jobtools/jncustomsearch.searchResults?in_organid=14160&in_jobDate=All&in_keyword=designer"]:
    st,b=get(u); print("TRY",st,len(b),u); 
    if b: print("TRYJOBS", len(set(re.findall(r'in_jnCounter=(\d+)',b))), [html.unescape(x)[:80] for x in re.findall(r'viewFullSingle[^"]*"[^>]*>([^<]{3,90})<',b)[:12]])
PY
