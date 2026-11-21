import sys, re
sys.path.insert(0, ".")
import connectors as C
for u in ["https://recruitment.macquarie.com/careers/JobDetail/Senior-Product-Designer/24875",
          "https://recruitment.macquarie.com/careers/JobDetail/Director-of-Product-Design/24818"]:
    d = C.get(u, tries=1).decode("utf8", "ignore")
    t = C.strip_html(d)
    i = t.find("Location")
    print("MQ", u[-6:], "| ld", bool(C.jsonld_job(d)), "|", re.sub(r"\s+", " ", t[max(0,i-200):i+300]) if i >= 0 else t[:600])
    for m in re.finditer(r"(Sydney|Melbourne|Brisbane|Perth|Australia|London|New York|Gurugram|Manila)", d): print("HIT", d[max(0,m.start()-120):m.end()+40].replace("\n"," ")); break
# Optus own site listing
for u in ["https://careers.optus.com.au/jobs", "https://careers.optus.com.au/search-jobs", "https://careers.optus.com.au/sitemap.xml"]:
    try:
        b = C.get(u, tries=1).decode("utf8","ignore"); print("OPT", u, len(b), re.findall(r'/[\w-]+/job/\d+', b)[:5], re.findall(r'<loc>[^<]{0,90}', b)[:5])
    except Exception as e: print("OPT", u, "ERR", e)
