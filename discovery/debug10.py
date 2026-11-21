import sys, re, json
sys.path.insert(0, ".")
import connectors as C, tagger as T
def show(name, gen, limit=40):
    try:
        n = 0
        for j in gen:
            n += 1
            if n <= limit:
                print("JOB", name, "|", j["title"][:60], "|", j["location"][:40], "|", T.discipline(j["title"], j["description"]),
                      "|", T.in_scope_location(j["location"], j.get("workplace", ""), j["description"]), "|", j["url"][:100], flush=True)
        print("DONE", name, n, flush=True)
    except Exception as e:
        print("ERR", name, type(e).__name__, str(e)[:150], flush=True)
show("acer", C.sf_rss("careers.acer.org", "ACER"))
show("coates", C.lever("coatesgroup", "Coates"))
show("breville", C.cornerstone("brevillesage", 1, "Breville"))
show("atari", C.greenhouse("atariinc", "Atari"))
show("riot", C.greenhouse("riotgames", "Riot Games"))
show("macquarie", C.avature("https://recruitment.macquarie.com/en_US/careers", "Macquarie Group"))
show("marsh", C.phenom("https://careers.marsh.com/global/en", "Marsh"))
show("ejjl", C.oracle("ejjl.fa.ap1.oraclecloud.com", "CX_1", "?"))
show("amp", C.oracle("fa-esow-saasfaprod1.fa.ocs.oraclecloud.com", "CX_1", "AMP"))
show("cfs", C.oracle("fa-eran-saasfaprod1.fa.ocs.oraclecloud.com", "CX_1", "Colonial First State"))
show("kmart", C.sf_rss("jobs.kmart.com.au", "Kmart Group"))
# identify the ejjl employer
try:
    d = C.get_json("https://ejjl.fa.ap1.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder="
                   + C.urllib.parse.quote('ById;Id="1005388",siteNumber=CX_1', safe=";=,"), headers={"Accept": "application/json"})
    it = (d.get("items") or [{}])[0]
    print("EJJL", it.get("Title"), "|", it.get("Organization"), "|", it.get("BusinessUnitName"), "|", it.get("LegalEmployer"), "|", it.get("PrimaryLocation"), "|", (C.strip_html(it.get("ExternalDescriptionStr") or ""))[:300])
except Exception as e:
    print("EJJL ERR", e)
for u in ["https://careers.optus.com.au/product-designer/job/176762", "https://careers.optus.com.au/",
          "https://salientgroup.com.au/wp-json/", "https://salientgroup.com.au/job-opportunities/",
          "https://employmenthero.com/jobs/position/betashares-product-designer-l2yc3/",
          "https://www.livehire.com/careers/bcf/job/AEKEA/0J2IIJ1JGX/digital-content-designer-bcf"]:
    try:
        b = C.get(u, tries=1).decode("utf8", "ignore")
        routes = []
        if "wp-json" in u:
            routes = [r for r in json.loads(b).get("routes", {}) if re.search("job|vacanc|position|opportunit", r)][:8]
        print("URL", u, len(b), routes, "| ld", "JobPosting" in b, "|",
              re.findall(r'api[\w.-]*\.(?:livehire|employmenthero)[^"\' ]{0,80}|/api/[\w/.-]{3,60}|"organisation(?:_|Id|Slug)?"\s*:\s*"?[\w-]{2,40}|myworkdayjobs[^"\']{0,60}|phenom[^"\']{0,40}|successfactors|jobs2web|avature|<title>[^<]{0,80}', b)[:12], flush=True)
    except Exception as e:
        print("URL", u, "ERR", e, flush=True)
