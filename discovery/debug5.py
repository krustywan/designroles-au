import sys, re
sys.path.insert(0, ".")
import connectors as C
for u in ["https://anglicarewa.elmotalent.com.au/careers/default/jobs", "https://anglicarewa.elmotalent.com.au/careers/default/job",
          "https://anglicarewa.elmotalent.com.au/careers/default/job/list"]:
    try:
        b = C.get(u, tries=1).decode("utf8", "ignore")
        links = sorted(set(re.findall(r'/job/view/\d+', b)))
        print("ELMO", u, len(b), re.findall(r"<title>[^<]{0,70}", b)[:1], len(links), links[:5], flush=True)
        for m in re.finditer(r'/job/view/(\d+)[^>]*>\s*([^<]{3,90})<', b):
            print("  E", m.group(1), m.group(2).strip())
    except Exception as e:
        print("ELMO", u, "ERR", e, flush=True)
b = C.get("https://beachamgroup.com/latest-jobs/").decode("utf8", "ignore")
for m in re.finditer(r"refari", b):
    print("REF", re.sub(r"\s+", " ", b[max(0, m.start()-200):m.start()+250]))
    break
print("REFCFG", re.findall(r"(?:agency|client|company|token|key|slug)[\"']?\s*[:=]\s*[\"'][\w-]{4,60}[\"']", b)[:10])
