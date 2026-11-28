#!/usr/bin/env bash
python3 - <<'PY'
import re, json, urllib.request, urllib.parse, concurrent.futures as cf
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36","Accept":"text/html,application/xhtml+xml,application/json","Accept-Language":"en-AU,en;q=0.9"}
def get(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=25); return r.geturl(), r.read().decode("utf8","ignore")
def show(n,u,pat=None,ctx=0):
    try:
        fu,b=get(u); t=re.search(r"<title>(.*?)</title>",b,re.S)
        ext=sorted(set(urllib.parse.urlparse(l).hostname for l in re.findall(r'(?:href|src|action|data-url)=["\'](https?://[^"\']+)',b)))
        ext=[h for h in ext if h and not re.search(r'facebook|instagram|linkedin|twitter|youtube|google|fonts|cdn|gstatic|doubleclick|tiktok|apple|vimeo|cloudfront|hotjar|onetrust|cookie|segment|optimizely|typekit|jsdelivr|unpkg|akamai|adobe|demdex|newrelic|sentry|clarity|bing|pinterest|cloudflare|recaptcha|wistia|hubspot|gravatar|w3\.org|schema\.org|x\.com',h)]
        out=f"{n} | {fu[:80]} | {t.group(1).strip()[:50] if t else ''} | len {len(b)} | ext {ext[:14]}"
        if pat: out+=" | M "+str(sorted(set(re.findall(pat,b)))[:8])
        if ctx and pat:
            m=re.search(pat,b); out+=" | C "+(re.sub(r"\s+"," ",b[max(0,m.start()-ctx):m.end()+ctx]) if m else "")
        return out
    except Exception as e: return f"{n} | {u} | ERR {str(e)[:70]}"
J=[
("Atlassian API","https://www.atlassian.com/endpoint/careers/listings",r'"title":"[^"]{0,60}"'),
("Endeavour","https://endeavourgroupcareers.com.au/",None),("Endeavour jobs","https://endeavourgroupcareers.com.au/jobs",r'(?:myworkdayjobs|successfactors|pageup|smartrecruiters|livehire|workday)[^"\']{0,60}'),
("Silver Chain","https://careers.silverchain.org.au/",r'(?:myworkdayjobs|successfactors|pageup|smartrecruiters|livehire|elmotalent|bigredsky|applynow|nga\.net)[^"\']{0,60}'),
("Mitti","https://mitti.com/",None),("SafetyCulture","https://safetyculture.com/",r'mitti[^"\']{0,40}'),
("Rest SR","https://rest.com.au/why-rest/about-rest/careers/open-opportunities",r'data-company[^>]{0,80}|company["\']?\s*[:=]\s*["\'][A-Za-z0-9_-]+'),
("Smith Family","https://jobs.thesmithfamily.com.au/search",r'company=[A-Za-z0-9_]+'),
("Smith Family rss","https://jobs.thesmithfamily.com.au/services/rss/job/?locale=en_GB&keywords=",r'<title>[^<]{0,60}'),
("Mantel tt","https://careers.mantelgroup.com.au/jobs.rss",r'<title>[^<]{0,60}'),
("WA Health","https://www.health.wa.gov.au/Careers/Search-our-jobs",r'https?://[a-z0-9.-]*bigredsky[^"\']{0,80}'),
("Officeworks","https://www.officeworks.com.au/campaigns/careers",None),("Officeworks2","https://careers.officeworks.com.au/jobs",None),
("Aware","https://aware.com.au/about-us/careers",None),("Linktree","https://linktr.ee/about/careers",r'(?:ashby|greenhouse|lever|workable)[^"\']{0,60}'),
("David Jones","https://www.davidjones.com/careers",r'(?:careers|jobs)\.[a-z0-9.-]+'),("UniSuper","https://www.unisuper.com.au/about-us/careers",r'(?:careers|jobs|apply)[a-z0-9.-]*\.[a-z0-9.-]+/[^"\']{0,40}'),
("Cbus","https://www.cbussuper.com.au/about-us/careers",r'(?:careers|jobs)[a-z0-9.-]*\.[a-z0-9.-]+[^"\']{0,40}'),("ING","https://www.ing.com.au/careers.html",r'(?:careers|jobs)[a-z0-9.-]*\.[a-z0-9.-]+[^"\']{0,40}'),
("Bendigo","https://www.bendigoadelaide.com.au/careers/",r'href="[^"]*(?:job|vacanc|opportun)[^"]*"'),("Black Dog","https://www.blackdoginstitute.org.au/about/working-with-us/",r'href="[^"]*(?:job|vacanc|position|career)[^"]*"'),
("Deloitte","https://www.deloitte.com/au/en/careers/job-search.html",r'(?:myworkdayjobs|avature|successfactors|jobs2web|apply\.deloitte)[^"\']{0,60}'),
("Deloitte api","https://apply.deloitte.com.au/",None),("Slalom","https://www.slalom.com/au/en/careers",r'(?:myworkdayjobs|jobs\.slalom|greenhouse|lever|icims)[^"\']{0,60}'),
("SBS adlogic","https://sbs.clients3.adlogic.com.au/",None),("SBS","https://careers.sbs.com.au/",r'adlogic[^"\']{0,80}'),
("Curtin jobadder","https://staff.curtin.edu.au/job-vacancies/",r'data-[a-z-]*key="[^"]+"|jobadder[^"\']{0,80}'),
("Cancer Vic","https://cancer-council-vic.applynow.net.au/",r'href="[^"]*/jobs/[^"]*"'),
("IBM avature","https://ibmglobal.avature.net/en_US/careers/SearchJobs?jobRecordsPerPage=6&location=Australia",r'/careers/JobDetail/[^"]{0,60}'),
("Atlassian icims","https://careers-apac-atlassian.icims.com/jobs/search?ss=1&in_iframe=1",r'/jobs/\d+/[^"]{0,50}'),
("Dept gh AU","https://boards-api.greenhouse.io/v1/boards/dept/jobs",r'"name":"[^"]*(?:Australia|Sydney|Melbourne)[^"]*"'),
("Nous gh","https://boards-api.greenhouse.io/v1/boards/nousgroup/jobs",r'"name":"[^"]{0,40}"'),
("Rokt wk","https://apply.workable.com/api/v1/widget/accounts/rokt",r'"(?:title|city|country)":"[^"]{0,40}"'),
("Paper Giant","https://papergiant.net/careers",r'href="[^"]*(?:job|role|position|apply)[^"]*"'),("ThinkPlace","https://www.thinkplaceglobal.com/careers/",r'href="[^"]*(?:job|role|position|apply)[^"]*"'),("Humaan","https://www.humaan.com/careers",r'href="[^"]*(?:job|role|position|apply)[^"]*"'),
]
with cf.ThreadPoolExecutor(10) as ex:
    for r in ex.map(lambda x: show(*x, ctx=0), J): print("Q", r[:700])
PY
