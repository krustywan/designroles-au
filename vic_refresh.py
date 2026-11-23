"""Refresh vic_cache.json, the saved copy of Victorian Government roles.

careers.vic.gov.au blocks GitHub's computers, so the daily run can't read it directly. Run this from any computer the
site lets in (a normal home or office connection works), then commit vic_cache.json:

    python vic_refresh.py
"""
import json, datetime
import connectors as C

jobs = list(C.vic_gov())
saved = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
json.dump({"saved": saved, "jobs": jobs}, open(C.VIC_CACHE, "w"), indent=1)
print(f"Saved {len(jobs)} Victorian Government candidates to vic_cache.json ({saved} Perth time)")
