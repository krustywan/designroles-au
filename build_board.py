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

def white_only_svg(path):
    """True when an SVG logo only uses white, so it needs a dark tile to be visible."""
    if not path.endswith(".svg"):
        return False
    import re
    cols = {c.lower() for c in re.findall(r'(?:fill|stroke|stop-color)\s*[=:]\s*"?\s*(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)', open(path, encoding="utf8", errors="ignore").read())}
    cols -= {"none", "null", "transparent", "currentcolor", "inherit"}
    return bool(cols) and cols <= {"#fff", "#ffffff", "white", "#ffffffff"}


for j in d["jobs"]:
    j["logo_dark"] = bool(j["logo"]) and white_only_svg(j["logo"])
data = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
open("board.html", "w").write(open("board_template.html").read().replace("__COIL__", "assets/coil.webp").replace("__DATA__", data))
print("board.html", len(data), "bytes of data,", d["count"], "roles,", sum(1 for j in d["jobs"] if j["logo"]), "with logos")
