#!/usr/bin/env bash
python3 - <<'PY'
import re, connectors as C
C.KEYWORDS[:] = ["designer"]
go = C._session()
orig = C._session
C._session = lambda: (lambda url, data=None, headers=None: (globals().__setitem__('LAST', go(url, data, headers)) or LAST))
for j in C.sa_gov(): break
k = LAST.find("Department of Human Services"); print("RAW", re.sub(r"\s+", " ", LAST[k-1500:k+900]))
for m in re.finditer(r"(?i)clos(e|ing)", LAST): print("CLOSE", re.sub(r"\s+"," ",LAST[m.start()-150:m.start()+200]))
PY
