#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request, urllib.parse, concurrent.futures as cf
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36","Accept":"text/html,application/xhtml+xml,application/json","Accept-Language":"en-AU,en;q=0.9"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25); return r.geturl(), r.read().decode("utf8","ignore")
ATS=r'(?:[a-z0-9-]+\.)?(?:myworkdayjobs\.com/[A-Za-z0-9_-]+|wd\d+\.myworkdaysite\.com/[^"\'\s]+|livehire\.com/careers/[a-z0-9-]+|teamtailor\.com|boards\.greenhouse\.io/[a-z0-9]+|job-boards\.greenhouse\.io/[a-z0-9]+|greenhouse\.io/embed/job_board\?for=[a-z0-9]+|jobs\.lever\.co/[a-z0-9-]+|jobs\.ashbyhq\.com/[A-Za-z0-9-]+|smartrecruiters\.com/[A-Za-z0-9-]+|pageuppeople\.com/(?:\d+|apply/\d+)|nga\.net\.au|taleo\.net|dayforcehcm\.com/[^"\'\s]*|apply\.workable\.com/[a-z0-9-]+|jobadder\.com|employmenthero\.com/[^"\'\s]{0,40}|successfactors\.(?:com|eu)[^"\'\s]{0,40}|bamboohr\.com|recruitee\.com|elmotalent\.com\.au|oraclecloud\.com[^"\'\s]{0,60}|avature\.net|jobvite\.com/[a-z0-9-]+|icims\.com|adlogic\.com\.au|applynow\.net\.au|humanforce|scouttalent|martianlogic|myrecruitmentplus|cvmail|mercury\.com\.au|eightfold\.ai|phenompeople|careers-page\.com|rippling|personio|breezy\.hr|bigredsky|seek\.com\.au/[^"\'\s]{0,40}|expr3ss|vacancyfiller|livevacancies|pinpointhq\.com|gethired|cornerstoneondemand|csod\.com)'
E=[
("Atlassian","https://www.atlassian.com/company/careers/all-jobs"),("WiseTech Global","https://www.wisetechglobal.com/careers/"),("SafetyCulture","https://safetyculture.com/careers/"),("Rokt","https://www.rokt.com/careers"),("Linktree","https://linktr.ee/about/careers"),("Dovetail","https://dovetail.com/careers/"),("Employment Hero","https://employmenthero.com/careers/"),("Domain","https://www.domain.com.au/group/careers/"),("Finder","https://www.finder.com.au/careers"),
("Endeavour Group","https://www.endeavourgroup.com.au/careers"),("David Jones","https://www.davidjones.com/careers"),("Country Road Group","https://www.countryroadgroup.com.au/careers"),("Officeworks","https://careers.officeworks.com.au/"),("Temple & Webster","https://www.templeandwebster.com.au/careers"),("Aesop","https://www.aesop.com/au/r/careers"),
("UniSuper","https://www.unisuper.com.au/about-us/careers"),("Aware Super","https://aware.com.au/careers"),("Rest","https://rest.com.au/about-rest/careers"),("Cbus","https://www.cbussuper.com.au/about-us/careers"),("ING","https://www.ing.com.au/careers.html"),("Bendigo","https://www.bendigoadelaide.com.au/careers/"),("Allianz","https://www.allianz.com.au/about-us/careers.html"),
("Beyond Blue","https://www.beyondblue.org.au/about/careers"),("Black Dog Institute","https://www.blackdoginstitute.org.au/about/careers/"),("Orygen","https://www.orygen.org.au/About/Careers"),("headspace","https://headspace.org.au/our-organisation/careers/"),("Cancer Council NSW","https://www.cancercouncil.com.au/careers/"),("Cancer Council Vic","https://www.cancervic.org.au/about/careers"),("The Smith Family","https://www.thesmithfamily.com.au/about-us/careers"),("World Vision","https://www.worldvision.com.au/about-us/careers"),("Red Cross","https://www.redcross.org.au/careers/"),("WA Health","https://www.health.wa.gov.au/Careers"),("Silver Chain","https://www.silverchain.org.au/careers/"),
("Deloitte","https://www.deloitte.com/au/en/careers.html"),("Mantel Group","https://mantelgroup.com.au/careers/"),("Slalom","https://www.slalom.com/au/en/careers"),("Nous Group","https://nousgroup.com/careers"),("Paper Giant","https://papergiant.net/careers"),("ThinkPlace","https://www.thinkplaceglobal.com/careers"),("Liquid Interactive","https://www.liquidinteractive.com.au/careers"),("Dept","https://www.deptagency.com/careers/"),("IBM","https://www.ibm.com/careers/search?field_keyword_05[0]=Australia"),("Publicis Sapient","https://careers.publicissapient.com/"),("Humaan","https://humaan.com/careers/"),
("SBS","https://careers.sbs.com.au/"),("UTS","https://www.uts.edu.au/about/careers"),("UTS jobs","https://jobs.uts.edu.au/"),("QUT","https://www.qut.edu.au/about/careers"),("Curtin","https://staff.curtin.edu.au/job-vacancies/"),
]
def probe(n,u):
    try:
        fu,b=get(u)
    except Exception as e:
        return f"{n} | ERR {str(e)[:60]}"
    hits=set(m.lower() for m in re.findall(ATS,b))
    sub=[]
    if not hits:
        host=urllib.parse.urlparse(fu).hostname
        cands=[l for l in re.findall(r'href=["\']([^"\'#]+)["\']',b) if re.search(r'job|career|vacanc|opportunit|position|join',l,re.I)]
        cands=[urllib.parse.urljoin(fu,l) for l in cands]
        cands=[l for l in dict.fromkeys(cands) if l.rstrip('/')!=fu.rstrip('/') and not re.search(r'facebook|linkedin|twitter|instagram|youtube|\.pdf',l)][:4]
        for c in cands:
            try:
                f2,b2=get(c); h2=set(m.lower() for m in re.findall(ATS,b2))
                if h2: sub.append(f"{c[:70]} -> {sorted(h2)[:3]}"); hits|=h2; break
                if urllib.parse.urlparse(f2).hostname!=host: sub.append(f"->{f2[:80]}")
            except Exception: pass
    return f"{n} | {fu[:70]} | {sorted(hits)[:4]} {sub[:2]}"
with cf.ThreadPoolExecutor(10) as ex:
    for r in ex.map(lambda x: probe(*x), E): print("P", r[:400])
# Direct API guesses for tech/studios
slugs=["atlassian","wisetechglobal","wisetech","safetyculture","rokt","linktree","dovetail","employmenthero","domain","domaingroup","finder","mantelgroup","mantel","dept","deptagency","slalom","papergiant","thinkplace","humaan","temple-webster","templeandwebster","finderau","nousgroup","aesop"]
def api(s):
    out=[]
    for name,u in [("gh",f"https://boards-api.greenhouse.io/v1/boards/{s}/jobs"),("lever",f"https://api.lever.co/v0/postings/{s}?mode=json"),("ashby",f"https://api.ashbyhq.com/posting-api/job-board/{s}"),("sr",f"https://api.smartrecruiters.com/v1/companies/{s}/postings?limit=1"),("workable",f"https://apply.workable.com/api/v1/widget/accounts/{s}")]:
        try:
            _,b=get(u); d=json.loads(b)
            c=len(d.get("jobs",[])) if isinstance(d,dict) and "jobs" in d else (len(d) if isinstance(d,list) else d.get("totalFound", "?"))
            if c not in (0,"0"): out.append(f"{name}:{c}")
        except Exception: pass
    return s, out
with cf.ThreadPoolExecutor(8) as ex:
    for s,o in ex.map(api, slugs):
        if o: print("API", s, o)
PY
