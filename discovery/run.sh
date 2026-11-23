#!/usr/bin/env bash
# Probe: which ways of asking careers.vic.gov.au get through from GitHub's computers?
set +e
U="https://www.careers.vic.gov.au/jobs?keywords=designer"
B="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
echo "curl plain UA:   $(curl -s -o /dev/null -w '%{http_code}' -A 'DesignRolesAU/1.0' $U)"
echo "curl browser UA: $(curl -s -o /dev/null -w '%{http_code}' -A "$B" -H 'Accept: text/html,application/xhtml+xml' -H 'Accept-Language: en-AU,en;q=0.9' $U)"
echo "curl http2+hdrs: $(curl -s --http2 -o /tmp/v.html -w '%{http_code}' -A "$B" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-AU,en;q=0.9' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: none' -H 'Sec-Fetch-Dest: document' -H 'Upgrade-Insecure-Requests: 1' $U) jobs=$(grep -c '/job/' /tmp/v.html)"
python3 - <<'PY'
import urllib.request
U="https://www.careers.vic.gov.au/jobs?keywords=designer"
for name,h in [("urllib bot UA",{"User-Agent":"DesignRolesAU-prototype/0.1 (design job aggregator; polite daily crawl)"}),
               ("urllib browser",{"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36","Accept":"text/html,application/xhtml+xml","Accept-Language":"en-AU,en;q=0.9"})]:
    try: r=urllib.request.urlopen(urllib.request.Request(U,headers=h),timeout=25); print(name, r.status)
    except Exception as e: print(name, e)
PY
pip -q install curl_cffi >/dev/null 2>&1 && python3 - <<'PY'
from curl_cffi import requests
r=requests.get("https://www.careers.vic.gov.au/jobs?keywords=designer", impersonate="chrome", timeout=25)
print("curl_cffi chrome", r.status_code, r.text.count('/job/'))
PY
echo "jina reader: $(curl -s -o /tmp/j.txt -w '%{http_code}' 'https://r.jina.ai/https://www.careers.vic.gov.au/jobs?keywords=designer') jobs=$(grep -c 'careers.vic.gov.au/job/' /tmp/j.txt)"
