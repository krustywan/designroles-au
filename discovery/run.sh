python3 - <<'PY'
import connectors as C
for name, fn in [("jobtools", lambda: C.vic_jobtools("14160", "Department of Families, Fairness and Housing")), ("bamboo", lambda: C.bamboohr("liv", "Law Institute of Victoria")), ("chemist", lambda: C.sf_rss("careers.chemistwarehouse.com", "Chemist Warehouse", "en_US"))]:
    try:
        js = list(fn()); print("RES", name, len(js))
        for j in js: print("JOB", name, "|", j["title"], "|", j["location"], "|", j.get("closes",""), "|", len(j["description"]), "|", j["url"][:110], "|", j["description"][:160].replace("\n"," "))
    except Exception as e: print("ERR", name, repr(e))
PY
