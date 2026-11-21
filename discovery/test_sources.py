"""Run each source in a sources file and report what it finds. Used by the probe workflow."""
import json, sys, time, traceback, os
sys.path.insert(0, ".")
import connectors as C, tagger as T

S = json.load(open(sys.argv[1]))
CALL = {
    "workday": lambda x: C.workday(x[0], x[1], x[2], x[3]),
    "oracle": lambda x: C.oracle(x[0], x[1], x[2]),
    "successfactors": lambda x: C.sf_rss(x[0], x[1], x[3] if len(x) > 3 else "en_US"),
    "pageup_site": lambda x: C.pageup_site(x[0], x[1]),
    "pageup": lambda x: C.pageup(x[0], x[1], x[2]),
    "smartrecruiters": lambda x: C.smartrecruiters(x[0], x[1]),
    "avature": lambda x: C.avature(x[0], x[1]),
    "radancy": lambda x: C.radancy(x[0], x[1]),
    "eightfold": lambda x: C.eightfold(x[0], x[1], x[2]),
    "phenom": lambda x: C.phenom(x[0], x[1]),
}
os.makedirs("discovery/out", exist_ok=True)
out = []
for plat, rows in S.items():
    if plat not in CALL:
        continue
    for x in rows:
        t0, n, keep, err, titles = time.time(), 0, 0, "", []
        try:
            for j in CALL[plat](x):
                n += 1
                if T.discipline(j["title"], j["description"]) and T.in_scope_location(j["location"], j.get("workplace", ""), j["description"]):
                    keep += 1
                    titles.append(j["title"][:50])
                    out.append(dict(j, sector=x[-1] if plat != "successfactors" else x[2]))
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:100]}"
        name = x[3] if plat == "workday" else x[2] if plat in ("oracle", "eightfold", "pageup") else x[1]
        print(f"TEST {plat:15} {str(name)[:28]:28} cand={n:3} kept={keep:2} {int(time.time()-t0):4}s {err} {titles[:3]}", flush=True)
json.dump(out, open("discovery/out/test_raw.json", "w"))
print("TOTAL kept", len(out))
