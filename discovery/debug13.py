import sys, re
sys.path.insert(0, ".")
import connectors as C
d = C.get("https://recruitment.macquarie.com/careers/JobDetail/Senior-Product-Designer/24875", tries=1).decode("utf8","ignore")
for m in re.finditer(r'field__label[^>]*>([^<]{0,60})<', d): print("MQL", repr(m.group(1).strip()))
i = d.find("Sydney"); print("MQCTX", re.sub(r"\s+"," ", d[i-700:i+50]))
for u in ["https://careers.optus.com.au/jobs", "https://careers.optus.com.au/jobs?page=2", "https://careers.optus.com.au/jobs?search=designer", "https://careers.optus.com.au/jobs?keywords=designer"]:
    b = C.get(u, tries=1).decode("utf8","ignore"); ids = re.findall(r'/[\w-]+/job/\d+', b)
    print("OPT", u, len(set(ids)), "designer" in b.lower(), list(dict.fromkeys(ids))[:3], re.findall(r'[?&](?:page|offset|p|start)=\d+', b)[:5], re.findall(r'\d+\s+(?:jobs|results|roles)', b)[:3])
for u in ["https://employmenthero.com/jobs/?q=designer", "https://employmenthero.com/jobs/"]:
    b = C.get(u, tries=1).decode("utf8","ignore")
    print("EH", u, len(b), re.findall(r'/jobs/position/[\w-]+', b)[:5], re.findall(r'https?://[\w.-]*api[\w.-]*/[\w/.-]{0,60}', b)[:8], re.findall(r'__NEXT_DATA__|buildId', b)[:2])
