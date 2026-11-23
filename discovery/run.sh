python3 - <<'PY'
import json, urllib.request, re
h = urllib.request.urlopen("https://krustywan.github.io/designroles-au/?x=2").read().decode()
m = re.search(r'const D = (\{.*?\});\n', h, re.S) or re.search(r'(\{"generated".*?\})\s*;?\s*\n', h, re.S)
d = json.loads(m.group(1).replace("<\\/", "</"))
for j in d["jobs"]:
    if not j.get("logo"): print("NOLOGO", j["employer"], "|", j["source"], "|", j["title"])
print("TOTAL", len(d["jobs"]), sum(1 for j in d["jobs"] if j.get("logo")))
PY
