python3 -c "
import os, fetch_logos as F
os.makedirs(F.OUT, exist_ok=True)
print('RESULT', F.one(('Airwallex','airwallex.com')))
"
mkdir -p discovery/out/a && cp logos/airwallex.com.* discovery/out/a/ 2>/dev/null; ls -la discovery/out/a
python3 - <<'PY'
import json, urllib.request, re
h = urllib.request.urlopen("https://krustywan.github.io/designroles-au/?x=4").read().decode()
d = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', h, re.S).group(1))
for j in d["jobs"]:
    if j["employer"] == "Airwallex": print("LOGO", j.get("logo"), j.get("logo_dark"))
PY
