#!/usr/bin/env bash
for u in "https://iworkfor.nsw.gov.au/jobs/all-keywords/all-agencies/all-organisations-entities/all-categories/all-locations/all-worktypes?keywords=designer" "https://iworkfor.sa.gov.au/" "https://www.jobs.act.gov.au/" "https://www.jobs.tas.gov.au/" "https://jobs.nt.gov.au/" "https://www.apsjobs.gov.au/"; do
  printf "GOV %s %s\n" "$(curl -s -L -o /tmp/g.html -w '%{http_code} %{size_download} %{url_effective}' --max-time 40 -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36' "$u")" "$u"
done
