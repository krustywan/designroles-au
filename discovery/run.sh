#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request
import connectors as C
real=C.candidate; C.candidate=lambda t: True
T=[("dovetail",lambda:C.ashby("dovetail","Dovetail")),("mitti",lambda:C.ashby("mitti","SafetyCulture")),
("wisetech",lambda:C.smartrecruiters("WiseTechGlobal","WiseTech Global")),("rest1",lambda:C.smartrecruiters("RestSuper","Rest")),("rest2",lambda:C.smartrecruiters("Rest","Rest")),("rest3",lambda:C.smartrecruiters("RetailEmployeesSuperannuationTrust","Rest")),
("crg-cw",lambda:C.pageup(433,"cw","Country Road Group")),("crg-caw",lambda:C.pageup(433,"caw","Country Road Group")),("wv-cw",lambda:C.pageup(530,"cw","World Vision")),("wv-caw",lambda:C.pageup(530,"caw","World Vision")),
("beyondblue",lambda:C.elmo("beyondblue.elmotalent.com.au","default","Beyond Blue")),("mantel",lambda:C.teamtailor("careers.mantelgroup.com.au","Mantel Group")),
("dept",lambda:C.greenhouse("dept","Dept")),("nous",lambda:C.greenhouse("nousgroup","Nous Group")),
("smith-us",lambda:C.sf_rss("jobs.thesmithfamily.com.au","The Smith Family","en_US")),("smith-gb",lambda:C.sf_rss("jobs.thesmithfamily.com.au","The Smith Family","en_GB"))]
for n,f in T:
    try:
        js=list(f()); print("R",n,len(js),"kept",[j["title"][:45] for j in js if real(j["title"])][:6],"| locs",list({j.get("location","")[:25] for j in js})[:4])
    except Exception as e: print("R",n,"ERR",repr(e)[:150])
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36","Accept":"*/*"}
def g(u): return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode("utf8","ignore")
d=json.loads(g("https://www.atlassian.com/endpoint/careers/listings")); L=d if isinstance(d,list) else d.get("postings") or d
print("ATL type",type(d).__name__, (list(d.keys())[:10] if isinstance(d,dict) else len(d)))
one=L[0] if isinstance(L,list) else None; print("ATL one", json.dumps({k:str(v)[:80] for k,v in one.items()}) if one else "")
au=[x for x in L if "Australia" in json.dumps(x.get("locations") or x.get("location") or "")] if isinstance(L,list) else []
print("ATL au",len(au),[x.get("title") for x in au if real(x.get("title",""))][:8])
w=json.loads(g("https://apply.workable.com/api/v1/widget/accounts/rokt")); print("WK keys",list(w.keys()), json.dumps({k:str(v)[:80] for k,v in w["jobs"][0].items()}))
b=g("https://endeavourgroupcareers.com.au/jobs"); print("END links",sorted(set(re.findall(r'href="([^"]*(?:/job/|/jobs/)[^"]*)"',b)))[:6], re.findall(r'(?:api|graphql|json)[^"\']{0,80}',b)[:6])
b=g("https://jobs.deloitte.com.au/"); print("DEL", re.search(r"<title>(.*?)</title>",b,re.S).group(1)[:60] if "<title>" in b else "", sorted(set(re.findall(r'(?:myworkdayjobs|avature|successfactors|jobs2web|pageup|smartrecruiters|oraclecloud|phenom|eightfold|cdn\.phenompeople)[^"\']{0,50}',b)))[:6], sorted(set(re.findall(r'href="([^"]*/job/[^"]*)"',b)))[:3])
b=g("https://staff.curtin.edu.au/job-vacancies/"); i=b.find("jobs.min.js"); print("CUR", re.sub(r"\s+"," ",b[max(0,i-900):i+300]))
PY
