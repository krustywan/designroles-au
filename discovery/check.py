import json
jobs = json.load(open("jobs.json"))
jobs = jobs.get("jobs", jobs) if isinstance(jobs, dict) else jobs
print("TOTAL", len(jobs))
want = ["acer", "coates", "breville", "atari", "riot", "macquarie", "marsh", "australiansuper", "amp", "colonial", "nsw", "mable", "siteminder", "kmart", "metcash", "super retail", "optus", "betashares", "salient", "merchantwise"]
for j in jobs:
    e = j["employer"].lower()
    if any(w in e for w in want):
        print("HAS", j["employer"][:34], "|", j["title"][:55], "|", j.get("location","")[:30], "|", j.get("link_type"), "|", j["url"][:80])
