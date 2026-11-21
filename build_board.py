import json, sys
d = json.load(open("jobs.json"))
# Safety net: if a run finds almost nothing (a site outage, a block), stop here so yesterday's board stays up.
if d["count"] < 5:
    sys.exit(f"Only {d['count']} roles found - not publishing. Check the 'Scrape the job sites' step log.")
data = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
open("board.html", "w").write(open("board_template.html").read().replace("__DATA__", data))
print("board.html", len(data), "bytes of data,", d["count"], "roles")
