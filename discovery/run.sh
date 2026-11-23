python3 - <<'PY'
import json, urllib.request
d = json.load(urllib.request.urlopen("https://krustywan.github.io/designroles-au/jobs.json?x=1"))
for j in d["jobs"]:
    if not j.get("logo"): print("NOLOGO", j["employer"], "|", j["source"], "|", j["title"], "|", j["url"])
PY
