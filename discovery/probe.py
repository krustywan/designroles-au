"""Find which hiring platform each company's careers site runs on.

Run on GitHub's computers (see .github/workflows/probe.yml). For each company it opens likely careers
pages, follows a few "search jobs" links, and looks for the fingerprints of known hiring platforms.
Prints one JSON line per company, prefixed with PROBE so the log is easy to filter.
"""
import csv, json, re, sys, time, html, urllib.request, urllib.parse, urllib.error, concurrent.futures as cf

UA = {"User-Agent": "Mozilla/5.0 (compatible; DesignRolesAU/0.1; +https://krustywan.github.io/designroles-au/)",
      "Accept": "text/html,application/xhtml+xml"}

SIGS = {
    "workday": r"https?://([\w-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([\w-]+)",
    "pageup": r"careers\.pageuppeople\.com/(\d+)/(\w+)/",
    "smartrecruiters": r"(?:jobs|careers)\.smartrecruiters\.com/([\w-]+)",
    "greenhouse": r"(?:boards|job-boards)\.greenhouse\.io/(?:embed/job_board\?for=)?([\w-]+)",
    "lever": r"jobs\.lever\.co/([\w.-]+)",
    "ashby": r"jobs\.ashbyhq\.com/([\w.%-]+)",
    "oracle": r"([\w-]+\.fa\.[\w.-]*oraclecloud\.com)/hcmUI/CandidateExperience/[\w-]+/sites/([\w]+)",
    "taleo": r"([\w-]+)\.taleo\.net",
    "nga": r"([\w-]+)\.nga\.net\.au",
    "icims": r"([\w-]+)\.icims\.com",
    "workable": r"apply\.workable\.com/([\w-]+)",
    "livehire": r"livehire\.com/(?:careers|widgets/job-listings)/([\w-]+)",
    "jobadder": r"(jobadder\.com)",
    "elmo": r"([\w-]+)\.elmotalent\.com\.au",
    "eightfold": r"(eightfold\.ai)",
    "phenom": r"(phenompeople|cdn\.phenompeople\.com|/global/en/job/)",
    "successfactors": r"(/services/rss/job|jobs2web|j2w\.|successfactors\.(?:com|eu))",
    "radancy": r"(tbcdn\.talentbrew\.com|talentbrew)",
    "avature": r"(avature\.net|/apply/JobDetail/|/careers/JobDetail/)",
    "pageup_site": r"(job-search-results-card|rec-marketing\.dc\d\.pageuppeople\.com)",
    "employmenthero": r"(employmenthero\.com/jobs/organisations/[\w-]+)",
    "bamboohr": r"([\w-]+)\.bamboohr\.com",
    "teamtailor": r"([\w-]+)\.teamtailor\.com",
    "cornerstone": r"([\w-]+)\.csod\.com",
    "dayforce": r"(jobs\.dayforcehcm\.com/[\w-]+/[\w-]+)",
}
SIGS = {k: re.compile(v, re.I) for k, v in SIGS.items()}
LINKWORDS = re.compile(r"search (all )?jobs|job search|current (jobs|opportunities|vacancies)|view (all )?(jobs|roles|opportunities)|"
                       r"open (roles|positions)|browse jobs|find (a )?(job|role)|explore (jobs|roles)|see (all )?(jobs|roles)|join us|careers?$|vacancies", re.I)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.geturl(), r.status, r.read(600_000).decode("utf8", "ignore")
    except urllib.error.HTTPError as e:
        return url, e.code, ""
    except Exception as e:
        return url, type(e).__name__, ""


def links(base, page):
    out = []
    for href, text in re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', page, re.S | re.I):
        text = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(text)).split())
        if LINKWORDS.search(text) or re.search(r"job|career|vacanc|opportunit", href, re.I):
            out.append(urllib.parse.urljoin(base, html.unescape(href)))
    return out


def probe(row):
    d = row["domain"]
    seeds = [f"https://careers.{d}", f"https://jobs.{d}", f"https://www.{d}/careers", f"https://{d}/careers",
             f"https://www.{d}/about-us/careers", f"https://www.{d}/about/careers", f"https://www.{d}/jobs"]
    found, visited, statuses, queue = {}, set(), {}, list(seeds)
    budget = 14
    while queue and budget > 0:
        u = queue.pop(0)
        if u in visited:
            continue
        visited.add(u)
        budget -= 1
        final, status, page = fetch(u)
        statuses[u] = status
        blob = final + " " + page
        for name, rx in SIGS.items():
            m = rx.search(blob)
            if m and name not in found:
                found[name] = {"match": m.group(0)[:160], "groups": list(m.groups()), "page": final}
        if any(k in found for k in ("workday", "pageup", "smartrecruiters", "greenhouse", "lever", "ashby", "oracle", "successfactors",
                                    "radancy", "avature", "pageup_site", "taleo", "nga", "eightfold", "phenom", "icims", "workable")):
            break
        if status == 200 and u in seeds:
            # follow a few promising links one level deeper, preferring other hosts (careers sites often live elsewhere)
            cand = [l for l in links(final, page) if l not in visited]
            cand.sort(key=lambda l: (urllib.parse.urlparse(l).netloc == urllib.parse.urlparse(final).netloc, len(l)))
            queue = cand[:4] + queue
        time.sleep(0.3)
    ok_pages = [u for u, s in statuses.items() if s == 200]
    blocked = [f"{u} {s}" for u, s in statuses.items() if s in (401, 403, 429, 503)]
    return dict(name=row["name"], sector=row["sector"], domain=d, found=found, ok=ok_pages[:3], blocked=blocked[:3])


if __name__ == "__main__":
    rows = list(csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else "discovery/companies.csv")))
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(probe, rows):
            print("PROBE " + json.dumps(r), flush=True)
