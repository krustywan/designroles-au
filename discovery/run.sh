#!/usr/bin/env bash
python3 - <<'PY'
import connectors as C, tagger as T
for name, fn in [("sa", C.sa_gov), ("nt", C.nt_gov)]:
    try:
        js = list(fn()); print("RES", name, len(js))
        for j in js: print("JOB", name, "|", j["title"], "|", j["employer"], "|", j["location"], "|", j["closes"], "|", j["employment_type"][:30], "|", j["salary_text"][:40], "|", len(j["description"]), "|", T.discipline(j["title"], j["description"]), "|", j["url"][:90])
    except Exception as e:
        import traceback; traceback.print_exc(); print("ERR", name, repr(e))
PY
