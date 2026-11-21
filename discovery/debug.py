import json, re, sys, urllib.request
sys.path.insert(0, ".")
import connectors as C
def wd(host, t, site):
    base = f"https://{host}/wday/cxs/{t}/{site}/jobs"
    for kw in ["designer", "design", "UX", ""]:
        body = json.dumps({"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": kw}).encode()
        try:
            d = json.loads(C.get(base, data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}))
            print("WD", t, repr(kw), "total", d.get("total"), [p.get("title") for p in d.get("jobPostings", [])][:6], flush=True)
        except Exception as e:
            print("WD", t, kw, "ERR", e)
for h, t, s in [("cba.wd3.myworkdayjobs.com", "cba", "CommBank_Careers"), ("telstra.wd3.myworkdayjobs.com", "telstra", "Telstra_Careers"),
                ("nbn.wd3.myworkdayjobs.com", "nbn", "nbncareers"), ("racwa.wd3.myworkdayjobs.com", "racwa", "RAC-WA")]:
    wd(h, t, s)
for u in ["https://www.nab.com.au/careers", "https://jobs.auspost.com.au/en_GB/careers/SearchJobs/feed/?search=designer",
          "https://jobs.auspost.com.au/en_GB/careers/SearchJobs/designer", "https://careers.origin energy.com.au".replace(" ", ""),
          "https://careers.originenergy.com.au/services/rss/job/?locale=en_US&keywords=designer",
          "https://careers.originenergy.com.au/search/?q=designer"]:
    try:
        b = C.get(u).decode("utf8", "ignore")
        print("URL", u, len(b), re.findall(r"eightfold[^\"']{0,80}|domain=[\w.]+|<item>|<title>[^<]{0,80}", b)[:8], flush=True)
    except Exception as e:
        print("URL", u, "ERR", e)
