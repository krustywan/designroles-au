import sys, re, json, urllib.parse
sys.path.insert(0, ".")
import connectors as C, tagger as T
from concurrent.futures import ThreadPoolExecutor
def show(name, fn):
    out = [f"START {name}"]
    try:
        n = 0
        for j in fn():
            n += 1
            d = T.discipline(j["title"], j["description"])
            if d: out.append(f"JOB {name} | {j['title'][:60]} | {j['location'][:35]} | {d} | {T.in_scope_location(j['location'], j.get('workplace',''), j['description'])} | {j['url'][:90]}")
        out.append(f"DONE {name} {n}")
    except Exception as e:
        out.append(f"ERR {name} {type(e).__name__} {str(e)[:150]}")
    return "\n".join(out)
tests = {
 "slater": lambda: C.cornerstone("slaterandgordon", 4, "Slater and Gordon"),
 "breville": lambda: C.cornerstone("brevillesage", 1, "Breville"),
 "disney": lambda: C.phenom("https://join.disneycareers.com/global/en", "Disney"),
 "marsh": lambda: C.phenom("https://careers.marsh.com/global/en", "Marsh"),
 "hcf": lambda: C.workday("hcf.wd105.myworkdayjobs.com", "hcf", "HCF_External_Career_Site", "HCF"),
 "simpro": lambda: C.workday("simpro.wd3.myworkdayjobs.com", "simpro", "simPRO_External_Careers", "Simpro"),
 "iress": lambda: C.workday("iress.wd3.myworkdayjobs.com", "iress", "IRESS_EXTERNAL", "Iress"),
 "resmed": lambda: C.workday("resmed.wd3.myworkdayjobs.com", "resmed", "ResMed_External_Careers", "ResMed"),
 "nbn": lambda: C.workday("nbn.wd3.myworkdayjobs.com", "nbn", "nbncareers", "NBN"),
 "cba": lambda: C.workday("cba.wd3.myworkdayjobs.com", "cba", "CommBank_Careers", "CBA"),
 "myob": lambda: C.lever("myob-2", "MYOB"),
 "envato": lambda: C.lever("envato-2", "Envato"),
 "zurich": lambda: C.sf_rss("www.careers.zurich.com", "Zurich"),
 "fujitsu": lambda: C.sf_rss("www.jobs.global.fujitsu.com", "Fujitsu"),
 "tfnsw": lambda: C.sf_rss("jobs.transport.nsw.gov.au", "Transport for NSW"),
 "woolies": lambda: C.avature("https://careers.woolworthsgroup.com.au/en_GB/apply", "Woolworths"),
 "auspost": lambda: C.avature("https://jobs.auspost.com.au/en_GB/careers", "Australia Post"),
 "lh-uon": lambda: C.listing_site("https://www.livehire.com/careers/universityofnewcastle/jobs", r"(?:https://www\.livehire\.com)?/careers/universityofnewcastle/job/[\w/-]+", "University of Newcastle", "livehire"),
 "lh-sca": lambda: C.listing_site("https://www.livehire.com/careers/supercheapauto/jobs", r"(?:https://www\.livehire\.com)?/careers/supercheapauto/job/[\w/-]+", "Supercheap", "livehire"),
 "wagov": C.wa_gov,
 "ebuu": lambda: C.oracle("ebuu.fa.ap1.oraclecloud.com", "CX", "?"),
 "hcgh": lambda: C.oracle("hcgh.fa.ap1.oraclecloud.com", "CX_3001", "?"),
 "ewlx": lambda: C.oracle("fa-ewlx-saasfaprod1.fa.ocs.oraclecloud.com", "CX_1", "?"),
}
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(lambda kv: show(*kv), tests.items()): print(r, flush=True)
for host, site, jid in [("ebuu.fa.ap1.oraclecloud.com","CX","74070"),("hcgh.fa.ap1.oraclecloud.com","CX_3001","5876"),("fa-ewlx-saasfaprod1.fa.ocs.oraclecloud.com","CX_1","1444")]:
    try:
        d = C.get_json(f"https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder=" + urllib.parse.quote(f'ById;Id="{jid}",siteNumber={site}', safe=";=,"), headers={"Accept":"application/json"})
        it = (d.get("items") or [{}])[0]
        print("ORA", host[:12], it.get("Title"), "|", it.get("PrimaryLocation"), "|", C.strip_html(it.get("ExternalDescriptionStr") or "")[:160])
    except Exception as e: print("ORA", host, "ERR", e)
for u in ["https://www.dfp.com.au/job/el1-assistant-director-design-strategist-689222", "https://www.dfp.com.au/wp-json/",
          "https://jobs.dayforcehcm.com/en-AU/qldcountry/116563/jobs/4273",
          "https://www.jobs.health.wa.gov.au/page.php?pageID=160&windowUID=0&AdvertID=423828",
          "https://career10.successfactors.com/career?company=cpaaustral&career_ns=job_listing_summary&resultType=XML",
          "https://careers.puffy.com/roles/cro-content-manager-ai-first",
          "https://careers.scopeaust.org.au/jobs/business-and-ux-analyst-hawthorn-vic-vic-australia",
          "https://www.airswift.com/jobs/principal-consultant-human-factors-1283390",
          "https://jobs.silkroad.com/RAA/RAACareers/jobs/3258", "https://jobs.silkroad.com/RAA/RAACareers",
          "https://readytech.currentjobs.co/job/product-discovery-lead/australia-remote/746",
          "https://careers.sbs.com.au/job-details/query/Product+Engagement+Strategist/in/Sydney/9840711/",
          "https://secure.workforceready.com.au/ta/6183760.careers?ShowJob=184669892&lang=en-AU",
          "https://www.rex.zone/jobs/product-generalist-jobs-sydney-2026"]:
    try:
        b = C.get(u, tries=1).decode("utf8", "ignore")
        ld = C.jsonld_job(b) or {}
        print("URL", u[:70], len(b), "| ld:", ld.get("employer"), "/", ld.get("title"), "/", ld.get("location"), "|",
              sorted(set(re.findall(r"pageuppeople|myworkdayjobs|successfactors|jobs2web|avature|phenom|greenhouse|lever\.co|ashbyhq|smartrecruiters|workable|teamtailor|jobadder|bullhorn|recruitcrm|livehire|dayforce|silkroad|currentjobs|ukg|wp-json|__NEXT_DATA__|/api/[\w/-]{3,40}|<item>|<Job>", b)))[:14], "|", re.findall(r"<title>[^<]{0,70}", b)[:1], flush=True)
    except Exception as e:
        print("URL", u[:70], "ERR", str(e)[:100], flush=True)
