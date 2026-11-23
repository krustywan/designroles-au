python3 - <<'PY'
import json, urllib.request
d = json.load(urllib.request.urlopen("https://krustywan.github.io/designroles-au/jobs.json?x=3"))
for j in d["jobs"]: print("JOB", j["employer"], "|", j["source"], "|", j["title"], "|", j.get("closes",""), "|", j.get("first_seen",""))
PY
