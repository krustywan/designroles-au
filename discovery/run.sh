#!/usr/bin/env bash
python3 - <<'PY'
import re, urllib.request, concurrent.futures as cf
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
E={"Domain":"domain.com.au","Linktree":"linktr.ee","Tyro":"tyro.com","Employment Hero":"employmenthero.com","Temple & Webster":"templeandwebster.com.au","Mecca":"mecca.com","Bendigo Bank":"bendigoadelaide.com.au","Allianz":"allianz.com.au","ABC":"abc.net.au","SBS":"sbs.com.au","Foxtel":"foxtel.com.au","JB Hi-Fi":"jbhifi.com.au","Officeworks":"officeworks.com.au","Deloitte":"deloitte.com","UTS":"uts.edu.au","QUT":"qut.edu.au","Curtin":"curtin.edu.au","Healthscope":"healthscope.com.au","Ramsay":"ramsayhealth.com.au","Fortescue":"fortescue.com","RACQ":"racq.com.au","Hostplus":"hostplus.com.au","Sydney Water":"sydneywater.com.au","ECU":"ecu.edu.au"}
ATS=r'(myworkdayjobs\.com/[^"\'\s<>]+|[a-z0-9-]+\.nga\.net\.au[^"\'\s<>]*|[a-z0-9-]+\.teamtailor\.com|apply\.workable\.com/[a-z0-9-]+|jobs\.lever\.co/[a-z0-9-]+|boards\.greenhouse\.io/[a-z0-9-]+|job-boards\.greenhouse\.io/[a-z0-9-]+|jobs\.ashbyhq\.com/[a-z0-9-]+|[a-z0-9-]+\.pageuppeople\.com[^"\'\s<>]*|careers\.pageuppeople\.com/\d+|successfactors\.(?:com|eu)[^"\'\s<>]*|jobs\.smartrecruiters\.com/[A-Za-z0-9-]+|[a-z0-9-]+\.taleo\.net[^"\'\s<>]*|dayforcehcm\.com[^"\'\s<>]*|jobs\.employmenthero\.com/[^"\'\s<>]+|[a-z0-9-]+\.livehire\.com|oraclecloud\.com/hcmUI[^"\'\s<>]*|[a-z0-9-]+\.avature\.net|jobs\.jobvite\.com/[a-z0-9-]+|[a-z0-9-]+\.bamboohr\.com|[a-z0-9-]+\.elmotalent\.com\.au|[a-z0-9-]+\.recruitee\.com|[a-z0-9-]+\.applynow\.net\.au|careers\.[a-z0-9.-]+/job/)'
def probe(item):
    n,d=item; out=[]
    for u in [f"https://www.{d}/careers",f"https://{d}/careers",f"https://careers.{d}/",f"https://www.{d}/careers/",f"https://jobs.{d}/",f"https://www.{d}/about/careers",f"https://www.{d}/jobs",f"https://www.{d}/work-with-us",f"https://www.{d}/about-us/careers"]:
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25); b=r.read().decode('utf8','ignore'); fu=r.geturl()
            hits=sorted(set(re.findall(ATS,b+" "+fu)))
            out.append(f"{u} -> {fu} [{r.status}] {hits[:6]}")
            if hits: break
        except Exception as e: out.append(f"{u} ERR {str(e)[:50]}")
    return n,out
with cf.ThreadPoolExecutor(8) as ex:
    for n,out in ex.map(probe,E.items()):
        for o in out:
            if '[' in o or o==out[-1]: print("EMP",n,"|",o[:400])
PY
