python3 - <<'PY'
import re, urllib.request, html
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
b=urllib.request.urlopen(urllib.request.Request("https://jobs.careers.vic.gov.au/jobtools/jncustomsearch.searchResults?in_organid=14160&in_jobDate=All",headers=UA),timeout=40).read().decode('utf8','ignore')
for h in sorted(set(re.findall(r'(?:href|action)="([^"]+)"',b))):
    if 'searchResults' in h or 'page' in h.lower() or 'skip' in h.lower(): print("LINK", html.unescape(h)[:250])
for m in re.findall(r'[^<>]{0,60}(?:of \d+|results|jobs found|Page \d)[^<>]{0,60}',b)[:10]: print("COUNT", m.strip()[:150])
i=b.find('viewFullSingle'); print("ROW", re.sub(r'\s+',' ',b[i-1500:i+1200]))
PY
