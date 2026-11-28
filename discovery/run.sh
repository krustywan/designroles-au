#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request
import connectors as C
real=C.candidate; C.candidate=lambda t: True
T=[("atlassian",lambda:C.atlassian()),("rokt",lambda:C.workable("rokt","Rokt")),("finder",lambda:C.workable("finder","Finder")),
("wisetech",lambda:C.smartrecruiters("wisetechglobal","WiseTech Global")),("deloitte",lambda:C.sf_rss("jobs.deloitte.com.au","Deloitte","en_US")),("deloitte-gb",lambda:C.sf_rss("jobs.deloitte.com.au","Deloitte","en_GB")),
("endeavour",lambda:C.listing_site("https://endeavourgroupcareers.com.au/jobs?page={page}",r"/job/[\w-]+-jid-\d+","Endeavour Group","endeavour",3))]
for n,f in T:
    try:
        js=list(f()); print("R",n,len(js),"kept",[j["title"][:45] for j in js if real(j["title"])][:6],"| locs",list({j.get("location","")[:25] for j in js})[:4])
    except Exception as e: print("R",n,"ERR",repr(e)[:150])
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36","Accept":"*/*","Referer":"https://staff.curtin.edu.au/job-vacancies/"}
k="AU6_klpob7rbkadenmkicx2r7fya7a"
for u in [f"https://apps.jobadder.com/widgets/v1/jobs?key={k}",f"https://apps.jobadder.com/widgets/v1/{k}/jobs",f"https://apps.jobadder.com/widgets/v1/jobs/{k}"]:
    try: b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode("utf8","ignore"); print("JA",u[-40:],len(b),b[:300].replace("\n"," "))
    except Exception as e: print("JA",u[-40:],"ERR",e)
try:
    b=urllib.request.urlopen(urllib.request.Request("https://apps.jobadder.com/widgets/v1/jobs.min.js",headers=UA),timeout=30).read().decode("utf8","ignore"); print("JAJS",sorted(set(re.findall(r'["\'](/[a-z0-9/{}._-]*(?:job|search)[a-z0-9/{}._-]*)["\']',b,re.I)))[:15], re.findall(r'https?://[a-z0-9.-]+/[^"\']{0,40}',b)[:6])
except Exception as e: print("JAJS ERR",e)
PY
