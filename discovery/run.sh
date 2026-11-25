#!/usr/bin/env bash
mkdir -p discovery/out/all
python3 - <<'PY'
import json, re, urllib.request
h = urllib.request.urlopen("https://krustywan.github.io/designroles-au/?x=9").read().decode()
d = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', h, re.S).group(1))
seen = {}
for j in d["jobs"]:
    if j.get("logo"): seen[j["logo"]] = j["employer"]
for path, emp in seen.items():
    name = path.split("/")[-1]
    try:
        open("discovery/out/all/" + name, "wb").write(urllib.request.urlopen("https://krustywan.github.io/designroles-au/" + path).read())
        print("GOT", name, "|", emp)
    except Exception as e: print("ERR", name, e)
json.dump(seen, open("discovery/out/all/_map.json", "w"))
PY
