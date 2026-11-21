import sys, re
sys.path.insert(0, ".")
import connectors as C, tagger as T
for u, rx in [("https://www.dfp.com.au/jobs?page=1", r"/job/[a-z0-9-]+-\d+"), ("https://careers.scopeaust.org.au/jobs", r"/jobs/[a-z0-9]+(?:-[a-z0-9]+)+"), ("https://jobs.silkroad.com/RAA/RAACareers", r"/RAA/RAACareers/jobs/\d+"), ("https://jobs.silkroad.com/RAA/RAACareers/jobs", r"/RAA/RAACareers/jobs/\d+")]:
    try:
        b = C.get(u, tries=1).decode("utf8","ignore"); print("LIST", u, len(b), list(dict.fromkeys(re.findall(rx, b)))[:4], re.findall(r'href="([^"]{5,80})"', b)[20:32])
    except Exception as e: print("LIST", u, "ERR", e)
for name, fn in [("hcf", lambda: C.workday("hcf.wd105.myworkdayjobs.com","hcf","HCF_External_Career_Site","HCF")), ("resmed", lambda: C.workday("resmed.wd3.myworkdayjobs.com","resmed","ResMed_External_Careers","ResMed")), ("resmed-sr", lambda: C.smartrecruiters("ResMed","ResMed")), ("breville", lambda: C.cornerstone("brevillesage",1,"Breville"))]:
    try:
        for j in fn(): print("T", name, "|", j["title"], "|", j["location"][:30], "|", T.discipline(j["title"], j["description"]), "|", T.in_scope_location(j["location"], j.get("workplace",""), j["description"]), "|", j["url"][-35:])
    except Exception as e: print("ERR", name, e)
b = C.get("https://career10.successfactors.com/career?company=cpaaustral&career_ns=job_listing_summary&resultType=XML", tries=1).decode("utf8","ignore")
print("CPA", re.sub(r"\s+"," ", b[:1500]))
