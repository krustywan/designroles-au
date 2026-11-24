python3 - <<'PY'
import re, urllib.parse, connectors as C
base = "https://jobs.careers.vic.gov.au/jobtools/"
page = C.get(f"{base}jncustomsearch.searchResults?in_organid=14160&in_jobDate=All").decode("utf8","ignore")
print("P0", re.search(r"Displaying[^<]*", page).group(0), len(page.split('class="job-item"'))-1)
form = dict(re.findall(r'<INPUT TYPE="hidden" NAME="([^"]+)" VALUE="([^"]*)"', page, re.I))
print("FORMKEYS", sorted(form)[:60])
print("FORMTAG", re.search(r'<FORM[^>]*resultsform[^>]*>', page, re.I).group(0))
print("SUBMITJS", re.search(r'function submitHref\(\)\s*\{.*?\}', page, re.S).group(0)[:600])
form.update({"in_organid":"14160","in_pg":"20","in_nav":"next_set","in_jobDate":"All"})
p2 = C.get(base+"jncustomsearch.searchAction", data=urllib.parse.urlencode(form).encode()).decode("utf8","ignore")
d = re.search(r"Displaying[^<]*", p2); print("P1", d.group(0) if d else None, len(p2.split('class="job-item"'))-1, len(p2))
print("P1 titles", re.findall(r'in_jnCounter=\d+"[^>]*>\s*([^<]{3,80}?)\s*</a>', p2)[:25])
PY
