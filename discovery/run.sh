#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request, urllib.parse
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
def get(u, data=None, h=None):
    hh=dict(UA); hh.update(h or {})
    r=urllib.request.urlopen(urllib.request.Request(u,data=data,headers=hh),timeout=30); return r.geturl(), r.read().decode('utf8','ignore')
pages={"Mecca":"https://www.mecca.com/en-au/careers/","Hostplus":"https://hostplus.com.au/careers","Linktree":"https://linktr.ee/about/careers","Bendigo":"https://www.bendigoadelaide.com.au/careers/","JB":"https://www.jbhifi.com.au/pages/jobs","Ramsay":"https://www.ramsayhealth.com.au/en/ramsay-careers/","Curtin":"https://staff.curtin.edu.au/job-vacancies/","UTS":"https://www.uts.edu.au/about/careers-uts","Employment Hero":"https://employmenthero.com/careers/","Tyro":"https://careers.tyro.com/"}
for n,u in pages.items():
    try:
        fu,b=get(u); links=sorted(set(l for l in re.findall(r'(?:href|src|action)=["\'](https?://[^"\']+)',b) if not re.search(r'facebook|instagram|linkedin\.com/(?!jobs)|twitter|youtube|google|\.css|\.js|\.png|\.jpg|\.svg|\.woff|cdn|fonts',l)))
        ext=[l for l in links if urllib.parse.urlparse(l).hostname and not urllib.parse.urlparse(l).hostname.endswith(urllib.parse.urlparse(fu).hostname.split('.',1)[-1])]
        print("PG",n,fu,"|",[l[:120] for l in ext][:25])
        for m in set(re.findall(r'[a-z0-9.-]*(?:myworkdayjobs|livehire|teamtailor|ashbyhq|lever\.co|greenhouse|smartrecruiters|pageuppeople|nga\.net|taleo|dayforce|workable|jobadder|employmenthero|successfactors|bamboohr|recruitee|elmotalent|applynow|oraclecloud|avature|jobvite|icims)[a-z0-9./_?=&-]*',b)): print("ATS",n,m[:150])
    except Exception as e: print("PG",n,"ERR",str(e)[:80])
# Teamtailor RSS / JSON
for u in ["https://careers.tyro.com/jobs.rss","https://careers.tyro.com/jobs"]:
    try: fu,b=get(u); print("TT",u,len(b),b[:300].replace("\n"," "))
    except Exception as e: print("TT",u,"ERR",e)
# NGA ECU
for u in ["https://ecu.nga.net.au/cp/index.cfm?audiencetypecode=ext","https://ecu.nga.net.au/cp/index.cfm?event=jobs.listJobs&audiencetypecode=ext"]:
    try:
        fu,b=get(u); print("NGA",u,"->",fu,len(b)); print("NGALINKS",sorted(set(re.findall(r'href="([^"]*(?:jati|jobs\.|event=)[^"]*)"',b)))[:20])
        i=b.find('jati'); print("NGACTX",re.sub(r"\s+"," ",b[max(0,i-1200):i+800]))
    except Exception as e: print("NGA",u,"ERR",e)
# Taleo RACQ
for u in ["https://racq.taleo.net/careersection/RACQ_External/jobsearch.ftl","https://tas-healthscope.taleo.net/careersection/jobsearch.ftl"]:
    try:
        fu,b=get(u); print("TAL",u,"->",fu,len(b)); print("TALPORTAL",re.findall(r'portal["\']?\s*[:=]\s*["\']?(\d{6,})',b)[:3], re.findall(r'careersection/([^/"]+)/',b)[:5])
    except Exception as e: print("TAL",u,"ERR",e)
# Dayforce
for u in ["https://jobs.dayforcehcm.com/en-AU/sydneywater/candidateportal","https://jobs.dayforcehcm.com/api/geo/sydneywater/jobposting/search"]:
    try: fu,b=get(u); print("DF",u,"->",fu,len(b),b[:300].replace("\n"," "))
    except Exception as e: print("DF",u,"ERR",e)
PY
