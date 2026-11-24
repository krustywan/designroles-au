#!/usr/bin/env bash
python3 - <<'PY'
import re, connectors as C
C.KEYWORDS[:] = ["designer"]
go = C._session()
orig = C._session
C._session = lambda: (lambda url, data=None, headers=None: (globals().__setitem__('LAST', go(url, data, headers)) or LAST))
for j in C.sa_gov(): break
t = C.strip_html(re.sub(r"<script.*?</script>|<style.*?</style>", " ", LAST, flags=re.S))
for lab in ["Agency", "Closing", "Location", "Salary", "Job Ref", "Status"]:
    for m in list(re.finditer(lab, t))[:2]: print("CTX", lab, "|", t[max(0,m.start()-80):m.start()+160].replace("\n"," "))
PY
