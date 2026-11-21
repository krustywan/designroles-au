import sys, re
sys.path.insert(0, ".")
import connectors as C, xml.etree.ElementTree as ET
d = C.get("https://www.jobs.global.fujitsu.com/job/Consultant/11593-en_US", tries=2).decode("utf8","ignore")
ld = C.jsonld_job(d) or {}
print("FJ", ld.get("title"), "|", ld.get("location"), "|", ld.get("employment_type"))
print("FJDESC", (ld.get("description") or C.strip_html(d))[:3000])
root = ET.fromstring(C.get("https://career10.successfactors.com/career?company=cpaaustral&career_ns=job_listing_summary&resultType=XML"))
for j in root.iter("Job"):
    print("CPA", j.findtext("ReqId"), "|", j.findtext("JobTitle"), "|", j.findtext("Location"))
    if j.findtext("ReqId").strip() == "6527" or "Content Lead" in j.findtext("JobTitle"):
        print("CPADESC", C.strip_html(j.findtext("Job-Description") or "")[:3000])
