python3 - <<'PY'
import re, json, urllib.request, html
import connectors as C
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36","Accept":"text/html,application/json;q=0.9,*/*;q=0.8"}
def get(u):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40); b=r.read().decode('utf8','ignore'); return r.status,b
    except Exception as e: return str(e)[:120],''
for h,emp in [("careers.chemistwarehouse.com","Chemist Warehouse"),("careers.epa.vic.gov.au","EPA Victoria")]:
    try:
        js=list(C.sf_rss(h,emp,"en_US")); print("SF",h,len(js)); [print("SFJOB",j["title"],"|",j["location"],"|",j["url"]) for j in js[:60]]
    except Exception as e: print("SF ERR",h,e)
for u in ["https://www.peoplebank.com.au/job-details/product-designer-%E2%80%93-uxui-ai-computer-vision-robotics-in-web-development-ui-ux-jobs-1788269",
          "https://www.peoplebank.com.au/jobs","https://www.peoplebank.com.au/job-search?keywords=designer","https://www.peoplebank.com.au/jobs?keywords=designer"]:
    st,b=get(u); print("PB",st,len(b),u)
    if b:
        print("PB title", re.search(r"<title>(.*?)</title>",b,re.S).group(1).strip()[:120] if "<title>" in b else None)
        print("PB jsonld", len(re.findall(r'application/ld\+json',b)), "jobposting" , 'JobPosting' in b)
        print("PB links", sorted(set(re.findall(r'href="(/job-details/[^"]+)"',b)))[:8])
        print("PB forms", re.findall(r'<form[^>]*>',b)[:3])
st,b=get("https://liv.bamboohr.com/careers/list"); print("BB",st,b[:1500])
st,b=get("https://tne.t1cloud.com/T1Default/CiAnywhere/Web/TNE/OrganisationManagement/JobBoardEnquiry/Index?f=%24ORG.REC.EXJOBB.ENQ&h=z87nilH1TX&t=1BB1B52F&suite=CES")
print("T1",st,len(b)); print("T1 title", re.findall(r"<title>(.*?)</title>",b,re.S)[:1]); print("T1 snippets", [m[:160] for m in re.findall(r'[^<>]{0,80}(?:[Jj]ob|[Dd]esign)[^<>]{0,80}',b)[:15]])
st,b=get("https://jobs.careers.vic.gov.au/jobtools/jncustomsearch.viewFullSingle?in_organid=14160&in_jnCounter=226728009&in_jobDate=All&in_searchbox=YES&in_summary=S")
print("VJT",st,len(b)); t=re.sub(r"<[^>]+>"," ",re.sub(r"<script.*?</script>|<style.*?</style>","",b,flags=re.S)); print("VJT text", html.unescape(re.sub(r"\s+"," ",t))[:1500])
PY
