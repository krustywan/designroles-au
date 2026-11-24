python3 - <<'PY'
import re, urllib.parse, connectors as C
base = "https://jobs.careers.vic.gov.au/jobtools/"
page = C.get(f"{base}jncustomsearch.searchResults?in_organid=14160&in_jobDate=All").decode("utf8","ignore")
allt=[]
for off in (20,40,60):
    allt += re.findall(r'in_jnCounter=(\d+)"[^>]*>\s*([^<]{3,90}?)\s*</a>', page)
    form = dict(re.findall(r'<INPUT TYPE="hidden" NAME="([^"]+)" VALUE="([^"]*)"', page, re.I))
    form.update({"in_organid":"14160","in_pg":str(off),"in_nav":"next_set","in_jobDate":"All"})
    page = C.get(base+"jncustomsearch.searchAction", data=urllib.parse.urlencode(form).encode()).decode("utf8","ignore")
    d = re.search(r"Displaying[^<]*", page); print("PAGE", off, d.group(0) if d else None)
print("ALL", len(allt), len(set(allt)))
for jn,t in allt: 
    if 'esign' in t or jn=='226728009': print("HIT", jn, t)
st=C.get(base+"jncustomsearch.viewFullSingle?in_organid=14160&in_jnCounter=226728009").decode("utf8","ignore")
print("DETAIL closing", re.findall(r'[Cc]losing[^<]{0,80}', st)[:3])
PY
