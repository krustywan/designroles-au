import sys
sys.path.insert(0, ".")
import connectors as C, tagger as T
from concurrent.futures import ThreadPoolExecutor
def show(name, fn):
    out=[]
    try:
        for j in fn():
            out.append(f"T {name} | {j['title'][:60]} | {j['location'][:30]} | {T.discipline(j['title'], j['description'])} | {j['url'][-40:]}")
    except Exception as e: out.append(f"ERR {name} {e}")
    return "\n".join(out) or f"NONE {name}"
tests = {
 "slater": lambda: C.cornerstone("slaterandgordon", 4, "Slater and Gordon"),
 "woolies": lambda: C.avature("https://careers.woolworthsgroup.com.au/en_GB/apply", "Woolworths"),
 "auspost": lambda: C.avature("https://jobs.auspost.com.au/en_GB/careers", "Australia Post"),
 "uon": lambda: C.listing_site("https://www.livehire.com/careers/universityofnewcastle/jobs", r"(?:https://www\.livehire\.com)?/careers/universityofnewcastle/job/[\w/-]+", "UoN", "livehire"),
 "wagov": C.wa_gov, "fujitsu": lambda: C.sf_rss("www.jobs.global.fujitsu.com", "Fujitsu"),
 "hcgh": lambda: C.oracle("hcgh.fa.ap1.oraclecloud.com", "CX_3001", "?"),
 "nbn": lambda: C.workday("nbn.wd3.myworkdayjobs.com", "nbn", "nbncareers", "NBN"),
 "tfnsw": lambda: C.sf_rss("jobs.transport.nsw.gov.au", "TfNSW"),
}
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(lambda kv: show(*kv), tests.items()): print(r, flush=True)
for t in ["Group Research Enablement Manager", "Senior Associate Inclusive Products", "Service Improvement Specialist", "Survey Insights Analyst", "Communication Design Assistant", "Behavioural Scientists and Leaders", "Customer Listening Specialist", "Experience Improvement Specialist", "Practice Leader Customer Strategy and Experience", "Product Engagement Strategist", "Product Discovery Lead", "Venture & Proposition Lead", "Business and UX Analyst", "Principal Consultant - Human Factors", "EL1 Assistant Director- Design Strategist", "Research Associate", "Consultant"]:
    print("TAG", t, "|", C.candidate(t), "|", T.discipline(t, ""))
