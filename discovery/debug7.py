import sys, re, json
sys.path.insert(0, ".")
import connectors as C
d = json.loads(C.get("https://beachamgroup.com/wp-json/"))
routes = [r for r in d.get("routes", {}) if "refari" in r.lower() or "job" in r.lower()]
print("ROUTES", routes[:30])
for r in routes[:8]:
    if "(?P" in r:
        continue
    try:
        b = C.get("https://beachamgroup.com/wp-json" + r, tries=1).decode("utf8", "ignore")
        print("GET", r, len(b), b[:400].replace("\n", " "))
    except Exception as e:
        print("GET", r, "ERR", e)
