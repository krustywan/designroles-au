import sys
sys.path.insert(0, ".")
import connectors as C, xml.etree.ElementTree as ET
root = ET.fromstring(C.get("https://career10.successfactors.com/career?company=cpaaustral&career_ns=job_listing_summary&resultType=XML"))
for j in root.iter("Job"):
    if j.findtext("ReqId").strip() == "6527":
        print("CPADESC", C.strip_html(j.findtext("Job-Description") or "").replace("\n", " ")[:4000])
