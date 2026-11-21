# DesignRoles AU — prototype scraper

Pulls design and research roles from Australian employers' own careers sites and government job boards, tags them, and builds a single-page job board.

## Run it

```bash
python3 run.py          # scrape every source in sources.json → raw.json + jobs.json
python3 build_board.py  # jobs.json → board.html (self-contained page)
```

Python 3.10+, standard library only. One run takes about 10 minutes, because of the polite delays between requests.

## Files

| File | What it does |
| --- | --- |
| `sources.json` | Employers and portals to crawl, grouped by hiring platform |
| `connectors.py` | One connector per platform: Greenhouse, Lever, Ashby, SmartRecruiters, PageUp (RSS), Workday, SuccessFactors (RSS), Radancy, Avature, WA and Victorian government boards, Remotive |
| `tagger.py` | Rule-based tagging: discipline, seniority, people leader, state, work mode, employment type, advertised pay, recruiter flag |
| `run.py` | Runs the connectors, filters to Australian/APAC-remote design roles, de-duplicates, tags, writes `jobs.json` |
| `board_template.html` / `build_board.py` | The board page; data is embedded at build time |
| `pageup_scan.py` / `pageup_batch.py` | One-off discovery: finds PageUp-hosted employers with Australian design roles |

## Adding an employer

1. Find its careers platform (look at the apply link of any job ad).
2. Add one line to `sources.json` under that platform, with the employer's name and sector.
3. If the site sits on its own domain, allow that exact host in Claude's network settings first.

## Etiquette and limits

- Feeds and public job APIs first; HTML only where there is no feed.
- 0.6–1.5 s between requests, one run a day, a user-agent naming the project.
- Sites that challenge automated clients (e.g. CommBank's Workday behind Cloudflare) are skipped, not worked around.
- Seek, LinkedIn and Indeed are not scraped (their terms prohibit it).
- No personal details (recruiter names, emails, phones) are stored. The board shows a short summary and links to the original ad.

## Next steps

- Swap rule-based tagging for an AI pass (API key needed), keeping the rules as a fallback.
- Schedule `run.py` daily (GitHub Actions or a small server) and publish `board.html`.
- Add sources: APS Jobs (Salesforce site, needs its own connector), Queensland SmartJobs, NSW (blocks bots), IAG, Telstra, Westpac, more Workday tenants.
