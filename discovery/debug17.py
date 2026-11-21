import sys, re
sys.path.insert(0, ".")
import connectors as C
for u, rx in [("https://www.dfp.com.au/jobs?page=2", r"/job/[a-z0-9-]+-\d+"), ("https://www.dfp.com.au/jobs?keywords=design", r"/job/[a-z0-9-]+-\d+"), ("https://www.dfp.com.au/jobs?search=design", r"/job/[a-z0-9-]+-\d+"), ("https://www.dfp.com.au/jobs?q=design", r"/job/[a-z0-9-]+-\d+"),
              ("https://careers.scopeaust.org.au/", r"/jobs/[a-z0-9]+(?:-[a-z0-9]+)+"), ("https://careers.scopeaust.org.au/jobs/", r"/jobs/[a-z0-9]+(?:-[a-z0-9]+)+"), ("https://careers.scopeaust.org.au/search", r"/jobs/[a-z0-9]+(?:-[a-z0-9]+)+")]:
    try:
        b = C.get(u, tries=1).decode("utf8","ignore"); l = list(dict.fromkeys(re.findall(rx, b)))
        print("LIST", u, len(l), l[:3], "689222" in b, re.findall(r'\?[\w]*page[\w]*=\d+|[?&](?:keywords|search|q)=', b)[:4])
    except Exception as e: print("LIST", u, "ERR", e)
b = C.get("https://career10.successfactors.com/career?company=cpaaustral&career_ns=job_listing_summary&resultType=XML", tries=1).decode("utf8","ignore")
print("CPATAGS", sorted(set(re.findall(r"<([A-Za-z-]+)>", b))))
for m in re.finditer(r"<JobTitle><!\[CDATA\[(.*?)\]\]>", b): print("CPAT", m.group(1))
i = b.find("<Job-Description"); j = b.find("</Job-Description>")
print("CPAREST", re.sub(r"\s+"," ", b[j:j+900]))
