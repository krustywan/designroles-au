import sys, re, json
sys.path.insert(0, ".")
import connectors as C
p = C.get("https://nswconnect.csod.com/ux/ats/careersite/2/home?c=nswconnect").decode("utf8", "ignore")
print("PAGE", len(p), "token" in p, re.findall(r'[a-z0-9-]*\.?api\.csod\.com', p)[:5], re.findall(r'"cultureID"\s*:\s*\d+', p)[:2])
n = 0
for j in C.cornerstone("nswconnect", 2, "NSW Government"):
    n += 1
    print("JOB", j["title"], "|", j["location"], "|", j["url"], "|", len(j["description"]))
print("TOTAL", n)
