"""Connectors: one per hiring platform. Each yields raw job dicts in a common shape.

Raw shape:
  source, source_id, employer, title, url, location, description (text),
  posted (ISO date or ''), employment_type, workplace, salary_text, remote_flag
"""
import json, re, time, html, urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET

UA = {"User-Agent": "DesignRolesAU-prototype/0.1 (design job aggregator; polite daily crawl)"}
DELAY = 0.6  # seconds between requests to the same platform


def get(url, data=None, headers=None, timeout=25, tries=4):
    h = dict(UA)
    if headers:
        h.update(headers)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i < tries - 1:
                time.sleep(15 * (i + 1))
                continue
            raise
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def get_json(url, **kw):
    return json.loads(get(url, **kw))


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"(?i)<(br|/p|/li|/h\d|/div)[^>]*>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()



def jsonld_job(page):
    """Extract a schema.org JobPosting from a page, if present."""
    for blob in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page, re.S):
        try:
            d = json.loads(blob.strip())
        except Exception:
            continue
        for x in (d if isinstance(d, list) else d.get("@graph", [d])):
            if isinstance(x, dict) and x.get("@type") == "JobPosting":
                locs = x.get("jobLocation") or []
                locs = locs if isinstance(locs, list) else [locs]
                place = []
                for l in locs:
                    a = (l or {}).get("address") or {}
                    if isinstance(a, dict):
                        place.append(", ".join(v for v in [a.get("addressLocality"), a.get("addressRegion"), a.get("addressCountry") if isinstance(a.get("addressCountry"), str) else ""] if v))
                sal = ""
                bs = x.get("baseSalary") or {}
                v = (bs.get("value") or {}) if isinstance(bs, dict) else {}
                if isinstance(v, dict) and (v.get("minValue") or v.get("value")):
                    sal = f"${v.get('minValue') or v.get('value')} - ${v.get('maxValue') or v.get('value')} per {str(v.get('unitText','year')).lower()}"
                et = x.get("employmentType") or ""
                return dict(title=html.unescape(x.get("title", "")), description=strip_html(html.unescape(x.get("description", ""))),
                            posted=(x.get("datePosted") or "")[:10], location="; ".join(p for p in place if p),
                            employment_type=", ".join(et) if isinstance(et, list) else et, salary_text=sal,
                            workplace="Remote" if x.get("jobLocationType") == "TELECOMMUTE" else "")
    return None


# Broad title pre-filter so we only fetch details for plausible roles (keeps traffic light).
CANDIDATE = re.compile(
    r"design|\bux\b|\bui\b|user experience|customer experience|\bcx\b|research|"
    r"content strateg|ux writ|experience architect|human[- ]centred|human[- ]centered|"
    r"service design|insight|usability|interaction|creative|visual|brand|motion|illustrat|"
    r"accessibility|journey",
    re.I,
)


def candidate(title):
    return bool(CANDIDATE.search(title or ""))


# ---------------- Greenhouse ----------------
def greenhouse(token, employer):
    d = get_json(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true")
    for j in d.get("jobs", []):
        if not candidate(j.get("title")):
            continue
        yield dict(
            source="greenhouse", source_id=f"gh-{token}-{j['id']}", employer=employer,
            title=j.get("title", ""), url=j.get("absolute_url", ""),
            location=(j.get("location") or {}).get("name", ""),
            description=strip_html(html.unescape(j.get("content", ""))),
            posted=(j.get("updated_at") or "")[:10], employment_type="", workplace="",
            salary_text="", remote_flag=None,
        )


# ---------------- Lever ----------------
def lever(token, employer):
    d = get_json(f"https://api.lever.co/v0/postings/{token}?mode=json")
    for j in d:
        if not candidate(j.get("text")):
            continue
        cat = j.get("categories") or {}
        sal = j.get("salaryRange") or {}
        sal_text = ""
        if sal.get("min"):
            sal_text = f"{sal.get('currency','')} {sal.get('min')} - {sal.get('max')} {sal.get('interval','')}"
        yield dict(
            source="lever", source_id=f"lv-{token}-{j['id']}", employer=employer,
            title=j.get("text", ""), url=j.get("hostedUrl", ""),
            location=cat.get("location", "") or ", ".join(cat.get("allLocations") or []),
            description=j.get("descriptionPlain", "") + "\n" + strip_html(" ".join(
                (l.get("content") or "") for l in (j.get("lists") or []))),
            posted=time.strftime("%Y-%m-%d", time.gmtime((j.get("createdAt") or 0) / 1000)),
            employment_type=cat.get("commitment", ""), workplace=j.get("workplaceType", ""),
            salary_text=sal_text, remote_flag=None,
        )


# ---------------- Ashby ----------------
def ashby(token, employer):
    d = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true")
    for j in d.get("jobs", []):
        if not candidate(j.get("title")):
            continue
        comp = (j.get("compensation") or {}).get("compensationTierSummary") or ""
        locs = [j.get("location", "")] + [
            (s.get("location") or "") for s in (j.get("secondaryLocations") or [])]
        yield dict(
            source="ashby", source_id=f"ab-{token}-{j.get('id')}", employer=employer,
            title=j.get("title", ""), url=j.get("jobUrl", ""),
            location="; ".join([l for l in locs if l]),
            description=j.get("descriptionPlain", "") or strip_html(j.get("descriptionHtml", "")),
            posted=(j.get("publishedAt") or "")[:10], employment_type=j.get("employmentType", ""),
            workplace=j.get("workplaceType", "") or ("Remote" if j.get("isRemote") else ""),
            salary_text=comp, remote_flag=j.get("isRemote"),
        )


# ---------------- SmartRecruiters ----------------
def smartrecruiters(company, employer):
    offset = 0
    while True:
        d = get_json(f"https://api.smartrecruiters.com/v1/companies/{company}/postings?country=au&limit=100&offset={offset}")
        content = d.get("content", [])
        for j in content:
            if not candidate(j.get("name")):
                continue
            time.sleep(DELAY)
            try:
                det = get_json(f"https://api.smartrecruiters.com/v1/companies/{company}/postings/{j['id']}")
            except Exception:
                det = {}
            secs = ((det.get("jobAd") or {}).get("sections") or {})
            desc = "\n".join(strip_html((secs.get(k) or {}).get("text", "")) for k in
                             ("companyDescription", "jobDescription", "qualifications", "additionalInformation"))
            loc = j.get("location") or {}
            yield dict(
                source="smartrecruiters", source_id=f"sr-{company}-{j['id']}", employer=employer,
                title=j.get("name", ""),
                url=det.get("postingUrl") or f"https://jobs.smartrecruiters.com/{company}/{j['id']}",
                location=", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country", "").upper()] if x),
                description=desc, posted=(j.get("releasedDate") or "")[:10],
                employment_type=(j.get("typeOfEmployment") or {}).get("label", ""),
                workplace="Remote" if loc.get("remote") else ("Hybrid" if loc.get("hybrid") else ""),
                salary_text="", remote_flag=loc.get("remote"),
            )
        offset += 100
        if offset >= d.get("totalFound", 0):
            break
        time.sleep(DELAY)


# ---------------- PageUp (RSS) ----------------
NS = {"job": "http://pageuppeople.com/"}


def pageup(pid, brand, employer, base="https://careers.pageuppeople.com"):
    raw = get(f"{base}/{pid}/{brand}/en/rss")
    root = ET.fromstring(raw)
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        if not candidate(title):
            continue
        desc = (it.findtext("description") or "") + "\n" + strip_html(it.findtext("job:description", "", NS))
        pub = it.findtext("pubDate") or ""
        try:
            posted = time.strftime("%Y-%m-%d", time.strptime(pub[:16], "%a, %d %b %Y"))
        except Exception:
            posted = ""
        yield dict(
            source="pageup", source_id=f"pu-{pid}-{it.findtext('job:refNo', '', NS)}", employer=employer,
            title=title, url=it.findtext("link") or "", apply_url=it.findtext("job:applyLink", "", NS),
            location=it.findtext("job:location", "", NS),
            description=strip_html(desc), posted=posted,
            employment_type=it.findtext("job:workType", "", NS), workplace="",
            salary_text="", remote_flag=None,
        )


# ---------------- WA Government (search.jobs.wa.gov.au) ----------------
WA_QUERIES = ["designer", "user experience", "service design", "customer experience", "UX",
              "researcher", "human centred", "content design", "digital experience", "design lead"]


def wa_gov():
    seen = set()
    for q in WA_QUERIES:
        for page in (1, 2, 3):
            url = "https://search.jobs.wa.gov.au/en/jobs/search?" + urllib.parse.urlencode({"query": q, "page": page})
            h = get(url).decode("utf8", "ignore")
            cards = h.split('class="card job-search-results-card"')[1:]
            if not cards:
                break
            for c in cards:
                m = re.search(r'href="(https://search\.jobs\.wa\.gov\.au/jobs/[^"]+)">([^<]+)</a>', c)
                if not m:
                    continue
                link, title = m.group(1), html.unescape(m.group(2)).strip()
                if link in seen or not candidate(title):
                    continue
                seen.add(link)
                def span(cls):
                    mm = re.search(r'job-component-%s".*?<span[^>]*>\s*(.*?)\s*</span>' % cls, c, re.S)
                    return html.unescape(re.sub(r"<[^>]+>", "", mm.group(1))).strip() if mm else ""
                yield dict(
                    source="wa-gov", source_id="wa-" + link.rsplit("/", 1)[-1], employer=span("department") or "WA Government",
                    title=title, url=link, location=span("location") or "WA",
                    description="", posted="", employment_type=span("employment-type"), workplace="",
                    salary_text=span("salary") or span("level"), remote_flag=None, _needs_detail=True,
                )
            time.sleep(DELAY)


def wa_gov_detail(job):
    h = get(job["url"]).decode("utf8", "ignore")
    m = re.search(r'<div class="[^"]*job-description[^"]*"[^>]*>(.*?)</section>', h, re.S) or \
        re.search(r'<main[^>]*>(.*?)</main>', h, re.S)
    job["description"] = strip_html(m.group(1))[:12000] if m else ""
    sal = re.search(r"\$\s?\d{2,3}[,\d]*(?:\s*(?:-|–|to)\s*\$\s?\d{2,3}[,\d]*)?(?:\s*(?:pa|p\.a\.|per annum))?", job["description"])
    if sal:
        job["salary_text"] = sal.group(0)
    loc = re.search(r"job-component-location.*?<span[^>]*>\s*(.*?)\s*</span>", h, re.S)
    if loc:
        job["location"] = strip_html(loc.group(1))
    return job


# ---------------- Remotive (remote; keep only AU/APAC/worldwide-eligible) ----------------
def remotive():
    d = get_json("https://remotive.com/api/remote-jobs?category=design")
    for j in d.get("jobs", []):
        loc = j.get("candidate_required_location", "") or ""
        if not re.search(r"australia|apac|asia|oceania|worldwide|anywhere|new zealand", loc, re.I):
            continue
        yield dict(
            source="remotive", source_id=f"rm-{j['id']}", employer=j.get("company_name", ""),
            title=j.get("title", ""), url=j.get("url", ""), location=f"Remote ({loc})",
            description=strip_html(j.get("description", "")), posted=(j.get("publication_date") or "")[:10],
            employment_type=j.get("job_type", ""), workplace="Remote", salary_text=j.get("salary", ""),
            remote_flag=True,
        )


KEYWORDS = ["designer", "design", "user experience", "UX", "researcher", "service design",
            "customer experience", "content design", "CX", "human centred", "experience architect"]


# ---------------- Workday (public cxs API) ----------------
def workday(host, tenant, site, employer):
    seen = set()
    base = f"https://{host}/wday/cxs/{tenant}/{site}"
    for kw in KEYWORDS:
        offset = 0
        while offset < 100:
            body = json.dumps({"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": kw}).encode()
            d = json.loads(get(base + "/jobs", data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}))
            posts = d.get("jobPostings", [])
            for p in posts:
                path = p.get("externalPath", "")
                if path in seen or not candidate(p.get("title")):
                    continue
                seen.add(path)
                time.sleep(DELAY)
                try:
                    info = json.loads(get(base + path, headers={"Accept": "application/json"})).get("jobPostingInfo", {})
                except Exception:
                    info = {}
                locs = [info.get("location", "")] + (info.get("additionalLocations") or [])
                yield dict(
                    source="workday", source_id=f"wd-{tenant}-{path.rsplit('_', 1)[-1]}", employer=employer,
                    title=p.get("title", ""), url=info.get("externalUrl") or f"https://{host}/en-US/{site}{path}",
                    location="; ".join(l for l in locs if l) or p.get("locationsText", ""),
                    description=strip_html(info.get("jobDescription", "")), posted=info.get("startDate", "")[:10],
                    employment_type=info.get("timeType", ""), workplace="", salary_text="", remote_flag=None,
                )
            offset += 20
            if offset >= d.get("total", 0):
                break
            time.sleep(DELAY)
        time.sleep(DELAY)


# ---------------- SAP SuccessFactors career sites (RSS search) ----------------
def sf_rss(host, employer, locale="en_US"):
    seen = set()
    for kw in KEYWORDS:
        url = f"https://{host}/services/rss/job/?" + urllib.parse.urlencode({"locale": locale, "keywords": kw})
        root = ET.fromstring(get(url))
        for it in root.iter("item"):
            link = it.findtext("link") or ""
            title = (it.findtext("title") or "").strip()
            if link in seen or not candidate(title):
                continue
            seen.add(link)
            m = re.match(r"(.*)\(([^()]*)\)\s*$", title)
            loc = m.group(2) if m else ""
            title = m.group(1).strip() if m else title
            pub = it.findtext("pubDate") or ""
            try:
                posted = time.strftime("%Y-%m-%d", time.strptime(pub[:16], "%a, %d %b %Y"))
            except Exception:
                posted = ""
            yield dict(
                source="successfactors", source_id="sf-" + host + "-" + link.rstrip("/").rsplit("/", 1)[-1],
                employer=employer, title=title, url=link, location=loc,
                description=strip_html(it.findtext("description") or ""), posted=posted,
                employment_type="", workplace="", salary_text="", remote_flag=None,
            )
        time.sleep(DELAY)


# ---------------- Radancy / TalentBrew career sites (e.g. Bupa) ----------------
def radancy(host, employer):
    seen = set()
    for kw in KEYWORDS:
        h = get(f"https://{host}/search-jobs/{urllib.parse.quote(kw)}").decode("utf8", "ignore")
        for path, inner in re.findall(r'href="(/job/[^"]+)"[^>]*>(.*?)</a>', h, re.S):
            t = re.search(r"<h2[^>]*>(.*?)</h2>", inner, re.S)
            title = strip_html(t.group(1) if t else inner).split("\n")[0].strip()
            if path in seen or not candidate(title):
                continue
            seen.add(path)
            time.sleep(DELAY)
            try:
                d = get(f"https://{host}{path}").decode("utf8", "ignore")
            except Exception:
                continue
            ld = jsonld_job(d) or {}
            title = (ld.get("title") or title).split("\n")[0].strip()
            yield dict(
                source="radancy", source_id="rd-" + path.rsplit("/", 1)[-1], employer=employer,
                title=title, url=f"https://{host}{path}",
                location=ld.get("location") or path.split("/")[2].replace("-", " ").title(),
                description=ld.get("description", ""), posted=ld.get("posted", ""),
                employment_type=ld.get("employment_type", ""), workplace=ld.get("workplace", ""),
                salary_text=ld.get("salary_text", ""), remote_flag=None,
            )
        time.sleep(DELAY)


# ---------------- Victorian Government (careers.vic.gov.au) ----------------
def vic_gov():
    seen = set()
    for kw in KEYWORDS:
        h = get("https://www.careers.vic.gov.au/jobs?" + urllib.parse.urlencode({"keywords": kw})).decode("utf8", "ignore")
        for row in h.split('class="views-row"')[1:]:
            m = re.search(r'href="(/job/[^"]+)"><h3>(.*?)</h3>', row, re.S)
            if not m:
                continue
            path, title = m.group(1), strip_html(m.group(2))
            if path in seen or not candidate(title):
                continue
            seen.add(path)
            dept = re.search(r"</h3></a>\s*<p[^>]*>(.*?)</p>", row, re.S)
            def field(label):
                mm = re.search(r"<strong>%s:</strong></p>\s*<p>(.*?)</p>" % label, row, re.S)
                return strip_html(mm.group(1)) if mm else ""
            blurb = re.search(r"Applications close:.*?</p>\s*</div>.*?<p>(.*?)</p>", row, re.S)
            desc = strip_html(blurb.group(1)) if blurb else ""
            time.sleep(DELAY)
            try:
                d = get("https://www.careers.vic.gov.au" + path).decode("utf8", "ignore")
                main = re.search(r"<main[^>]*>(.*?)</main>", d, re.S)
                if main:
                    desc = strip_html(main.group(1))[:12000]
            except Exception:
                pass
            yield dict(
                source="vic-gov", source_id="vic-" + path.rsplit("-", 1)[-1],
                employer=strip_html(dept.group(1)) if dept else "Victorian Government",
                title=title, url="https://www.careers.vic.gov.au" + path,
                location=(field("Location") + ", VIC").strip(", "), description=desc, posted="",
                employment_type=field("Work Type"), workplace="", salary_text=field("Salary"), remote_flag=None,
            )
        time.sleep(DELAY)


# ---------------- Avature career sites (e.g. Woolworths Group) ----------------
def avature(base, employer):
    """base like https://careers.woolworthsgroup.com.au/en_GB/apply"""
    seen = set()
    for kw in KEYWORDS:
        root = ET.fromstring(get(f"{base}/search-jobs/feed/?" + urllib.parse.urlencode({"jobRecordsPerPage": 100, "search": kw})))
        for it in root.iter("item"):
            link = (it.findtext("link") or "").strip()
            title = (it.findtext("title") or "").strip()
            if link in seen or not candidate(title):
                continue
            seen.add(link)
            time.sleep(DELAY)
            try:
                d = get(link).decode("utf8", "ignore")
            except Exception:
                continue
            ld = jsonld_job(d) or {}
            def field(label):
                m = re.search(label + r"\s*</[^>]+>\s*(?:<[^>]+>\s*)*([^<]+)", d)
                return html.unescape(m.group(1)).strip() if m else ""
            brand = field("Brand")
            yield dict(
                source="avature", source_id="av-" + link.rstrip("/").rsplit("/", 1)[-1],
                employer=f"{employer} ({brand})" if brand and brand.lower() not in employer.lower() else employer,
                title=ld.get("title") or title, url=link,
                location=ld.get("location") or field("Location").rstrip(", "),
                description=ld.get("description", ""), posted=ld.get("posted", ""),
                employment_type=ld.get("employment_type") or field("Employment type"), workplace="",
                salary_text=ld.get("salary_text", ""), remote_flag=None,
            )
        time.sleep(DELAY)


# ---------------- Link resolution ----------------
TRACKING = re.compile(r"[?&](utm_[a-z]+|feedId|source)=[^&]*", re.I)


def clean_url(u):
    u = TRACKING.sub("", u or "")
    return u.replace("/?&", "/?").rstrip("?&")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def final_url(u, hops=5):
    """Follow redirects by hand so we can see where a job link really lands."""
    op = urllib.request.build_opener(_NoRedirect)
    for _ in range(hops):
        try:
            r = op.open(urllib.request.Request(u, headers=UA), timeout=15)
            return u, r.status
        except urllib.error.HTTPError as e:
            loc = e.headers.get("Location")
            if e.code in (301, 302, 303, 307, 308) and loc:
                u = urllib.parse.urljoin(u, loc)
                continue
            return u, e.code
        except Exception:
            return u, None  # host not reachable from here: can't verify
    return u, None


def resolve_link(job):
    """Return (url, link_type). link_type: 'ad' (the job's own page), 'apply' (its application form),
    'search' (employer's job search for this title), or 'unverified'."""
    url = clean_url(job["url"])
    end, status = final_url(url)
    path = urllib.parse.urlparse(end).path.strip("/")
    landed_on_home = path in ("", "en", "en-us", "jobs", "careers", "home", "home-page", "jobs/search") or len(path) < 4
    if status is None and not landed_on_home:
        return url, "unverified"
    if status == 200 and not landed_on_home:
        return end if urllib.parse.urlparse(end).netloc == urllib.parse.urlparse(url).netloc else url, "ad"
    host = urllib.parse.urlparse(end).netloc
    found = find_on_careers_site(host, job["title"]) if host else None
    if found:
        return found, "ad"
    if job.get("apply_url"):
        return job["apply_url"], "apply"
    host = urllib.parse.urlparse(end).netloc
    return f"https://{host}/jobs/search?" + urllib.parse.urlencode({"keywords": job["title"]}), "search"


def _norm(t):
    return re.sub(r"[^a-z0-9]+", " ", html.unescape(t or "").lower()).strip()


def find_on_careers_site(host, title):
    """PageUp employers that moved to their own 'Careers Site' (same platform as WA Gov):
    search the site for the title and return the matching job's own page."""
    try:
        h = get(f"https://{host}/jobs/search?" + urllib.parse.urlencode({"query": title}), tries=1, timeout=15).decode("utf8", "ignore")
    except Exception:
        return None
    want = _norm(title)
    cards = re.findall(r'href="(https://%s/jobs/(?!search)[^"]+)"[^>]*>([^<]+)</a>' % re.escape(host), h)
    for link, text in cards:
        if _norm(text) == want:
            return link
    loose = {link for link, text in cards if _norm(text).startswith(want) or want.startswith(_norm(text))}
    return loose.pop() if len(loose) == 1 else None


# ---------------- Queensland Government (smartjobs.qld.gov.au) ----------------
QLD = "https://smartjobs.qld.gov.au/jobtools/"


def qld_gov():
    seen = set()
    for kw in KEYWORDS:
        data = urllib.parse.urlencode({"in_organid": "14904", "in_skills": kw, "in_jobDate": "All", "in_sessionid": "",
                                       "in_version": "", "in_exact_phrase_match": "Y"}).encode()
        h = get(QLD + "jncustomsearch.searchResults", data=data).decode("utf8", "ignore")
        for li in h.split('<!--Summary Body')[1:]:
            m = re.search(r'HREF="(jncustomsearch\.viewFullSingle\?[^"]*in_jnCounter=(\d+)[^"]*)".*?<strong>(.*?)</strong>,?\s*([^<]*)</span>', li, re.S)
            if not m:
                continue
            counter, title, agency = m.group(2), strip_html(m.group(3)), strip_html(m.group(4))
            if counter in seen or not candidate(title):
                continue
            seen.add(counter)
            etype = re.search(r'<span class="type">(.*?)</span>', li, re.S)
            loc = re.search(r'class="locality">(.*?)</strong>', li, re.S)
            snippet = re.search(r'class="search-description">(.*?)</div>', li, re.S)
            url = f"{QLD}jncustomsearch.viewFullSingle?in_organid=14904&in_jnCounter={counter}"
            desc, sal = strip_html(snippet.group(1)) if snippet else "", ""
            time.sleep(DELAY)
            try:
                d = get(url).decode("utf8", "ignore")
                body = re.search(r'<div id="content">(.*?)<!-- End Content', d, re.S)
                desc = strip_html(body.group(1))[:12000] if body else desc
                s = re.search(r"Salary[^$]{0,80}(\$[\d,]+[^<]{0,60})", d)
                sal = strip_html(s.group(1)) if s else ""
            except Exception:
                pass
            yield dict(
                source="qld-gov", source_id="qld-" + counter, employer=agency or "Queensland Government",
                title=title, url=url, location=(strip_html(loc.group(1)) + ", QLD") if loc else "QLD",
                description=desc, posted="", employment_type=strip_html(etype.group(1)) if etype else "",
                workplace="", salary_text=sal, remote_flag=None,
            )
        time.sleep(DELAY)


# ---------------- Australian Public Service Gazette (APS Jobs vacancies, CC BY 4.0) ----------------
# Daily PDF published by the APS Commission. Licence: CC BY 4.0, EXCEPT contact persons' names,
# phone numbers and emails, which must not be reproduced, so we strip them.
import datetime, subprocess, tempfile, os

GAZETTE = "https://s3-ap-southeast-2.amazonaws.com/apsc.gazette/"
PERSONAL = re.compile(r"(?im)^.*(contact\s*(name|officer|person)|position contact|phone|telephone|mobile|e-?mail).*$|"
                      r"[\w.+-]+@[\w-]+\.[\w.]+|(?:\+?61|0)[2-478](?:[ -]?\d){8}")


def _gazette_pdf(day):
    """Fetch one day's Daily Gazette PDF. The issue number is the ISO week minus one; try neighbours too."""
    wk = day.isocalendar()[1]
    label = day.strftime("%A - ") + f"{day.day:02d} " + day.strftime("%B %Y")
    for n in (wk - 1, wk, wk - 2):
        name = f"PS{n} Daily Gazette {label}.pdf"
        try:
            return name, get(GAZETTE + urllib.parse.quote(name), tries=1)
        except Exception:
            continue
    return None, None


def _pdf_text(blob):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(blob)
        path = f.name
    try:
        return subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True, timeout=120).stdout
    finally:
        os.unlink(path)


LABELS = ["Job Title", "Job Type", "Location", "Salary", "Future Merit\nLocations", "Office\nArrangement\nDetails",
          "Office\nArrangement", "Classification", "Position Number", "Agency Website", "Job Description"]


def aps_gazette(days=21):
    today = datetime.date.today()
    seen = set()
    for back in range(days):
        day = today - datetime.timedelta(days=back)
        if day.weekday() >= 5:
            continue
        name, blob = _gazette_pdf(day)
        if not blob:
            continue
        for v in parse_gazette(_pdf_text(blob)):
            if v["vn"] in seen or not v["title"] or not candidate(v["title"]):
                continue
            try:
                if datetime.datetime.strptime(v["closing"].split(" ", 1)[1], "%d %B %Y").date() < today:
                    continue
            except Exception:
                pass
            seen.add(v["vn"])
            f = v["fields"]
            url = f["Job Description"] if f["Job Description"].startswith("http") else f["Agency Website"]
            yield dict(
                source="aps-gazette", source_id="aps-" + v["vn"], employer=v["agency"], title=v["title"],
                url=url or "https://www.apsjobs.gov.au/s/job-search", location=f["Location"],
                description=v["description"], posted=day.isoformat(),
                employment_type=f["Job Type"], workplace=f["Office\nArrangement"], salary_text=f["Salary"],
                remote_flag=None, apply_url="https://www.apsjobs.gov.au/s/job-search",
            )
        time.sleep(DELAY)


def parse_gazette(text):
    """Split a Daily Gazette's text into vacancies."""
    text = text.replace("\x0c", "\n")
    text = re.sub(r"(?m)^(Australian Public Service Gazette|PS\d+ Daily Gazette .*\.pdf|Page \d+ of \d+)[ \t]*$\n?", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    parts = re.split(r"\nVacancy (VN-\d+)\n", text)
    for k in range(1, len(parts) - 1, 2):
        vn, block, before = parts[k], parts[k + 1], parts[k - 1]
        # The closing date sits before or after the agency name, depending on page layout.
        header = block.split("\nJob Title\n", 1)[0]
        cm = re.search(r"Closing Date:([^\n]*)", header)
        head = re.sub(r"Closing Date:[^\n]*", "", header).strip().split("\n\n")[0]
        lines = [l.strip() for l in head.split("\n") if l.strip()]
        if not lines:
            # Other layout: "Portfolio / Agency / Division" sits just above the "Vacancy VN-" line.
            prev = [l.strip() for l in before.rstrip().rsplit("\n\n", 1)[-1].split("\n") if l.strip()]
            lines = prev
        AGENCY_WORDS = re.compile(r"Department|Agency|Authority|Commission|Office|Service|Bureau|Australian|National|Tribunal|"
                                  r"Court|Limited|Council|Institute|Museum|Gallery|Library|Archives|Centre|Board|Organisation|Corporation|Regulator")
        named = [i for i, l in enumerate(lines) if AGENCY_WORDS.search(l)]
        lines = lines[named[0]:] if named else lines
        agency = lines[0] if lines else ""
        if len(lines) > 1 and (len(agency) > 38 or lines[1][:1].islower() or agency.endswith((" and", " of", " for", " the"))):
            agency += " " + lines[1]  # the name wrapped onto a second line
        f = {}
        for lab in LABELS:
            m = re.search(r"\n%s\n\n(.*?)\n\n" % re.escape(lab), block, re.S)
            f[lab] = " ".join(m.group(1).split()) if m else ""
        m = re.search(r"\nJob Description\n\n\S+\n\n(.*)", block, re.S)
        desc = PERSONAL.sub("", m.group(1) if m else "")
        yield dict(vn=vn, agency=agency, closing=cm.group(1).strip() if cm else "", title=f["Job Title"],
                   fields=f, description=strip_html(desc)[:12000])
