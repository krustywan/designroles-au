import json, os, sys
d = json.load(open("jobs.json"))
# Safety net: if a run finds almost nothing (a site outage, a block), stop here so yesterday's board stays up.
if d["count"] < 5:
    sys.exit(f"Only {d['count']} roles found - not publishing. Check the 'Scrape the job sites' step log.")
# Attach a logo to each role when we have one for that employer (see fetch_logos.py).
domains = {k: v for k, v in json.load(open("employer_domains.json")).items() if not k.startswith("_")}
for j in d["jobs"]:
    dom = domains.get(j["employer"])
    j["logo"] = next((f"logos/{dom}.{ext}" for ext in ("png", "svg", "jpg", "ico") if dom and os.path.exists(f"logos/{dom}.{ext}")), "")
data = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
open("board.html", "w").write(open("board_template.html").read().replace("__DATA__", data))
print("board.html", len(data), "bytes of data,", d["count"], "roles,", sum(1 for j in d["jobs"] if j["logo"]), "with logos")
