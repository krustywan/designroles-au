"""Run every connector, keep Australian design/research roles, tag them and write jobs.json.

Usage: python3 run.py            (all sources in sources.json)
"""
import json, time, re, sys, traceback, hashlib
import summarise
import connectors as C
import tagger as T

SRC = json.load(open("sources.json"))
log = []


def tasks():
    """Every source as (name, sector, a function that yields its jobs)."""
    t = []
    for tok, emp, sec in SRC.get("greenhouse", []):
        t.append((f"greenhouse/{tok}", sec, lambda tok=tok, emp=emp: C.greenhouse(tok, emp)))
    for tok, emp, sec in SRC.get("lever", []):
        t.append((f"lever/{tok}", sec, lambda tok=tok, emp=emp: C.lever(tok, emp)))
    for tok, emp, sec in SRC.get("ashby", []):
        t.append((f"ashby/{tok}", sec, lambda tok=tok, emp=emp: C.ashby(tok, emp)))
    for tok, emp, sec in SRC.get("smartrecruiters", []):
        t.append((f"smartrecruiters/{tok}", sec, lambda tok=tok, emp=emp: C.smartrecruiters(tok, emp)))
    for pid, brand, emp, sec in SRC.get("pageup", []):
        t.append((f"pageup/{pid}", sec, lambda pid=pid, brand=brand, emp=emp: C.pageup(pid, brand, emp)))
    for host, tenant, site, emp, sec in SRC.get("workday", []):
        t.append((f"workday/{tenant}", sec, lambda h=host, te=tenant, si=site, emp=emp: C.workday(h, te, si, emp)))
    for host, site, emp, sec in SRC.get("oracle", []):
        t.append((f"oracle/{host.split('.')[0]}/{emp}", sec, lambda h=host, si=site, emp=emp: C.oracle(h, si, emp)))
    for host, emp, sec, loc in SRC.get("successfactors", []):
        t.append((f"successfactors/{host}", sec, lambda h=host, emp=emp, loc=loc: C.sf_rss(h, emp, loc)))
    for host, emp, sec in SRC.get("radancy", []):
        t.append((f"radancy/{host}", sec, lambda h=host, emp=emp: C.radancy(h, emp)))
    for base, emp, sec in SRC.get("avature", []):
        t.append((f"avature/{base.split('/')[2]}", sec, lambda b=base, emp=emp: C.avature(b, emp)))
    for home, emp, sec in SRC.get("phenom", []):
        t.append((f"phenom/{home.split('/')[2]}", sec, lambda h=home, emp=emp: C.phenom(h, emp)))
    for host, emp, sec in SRC.get("pageup_site", []):
        t.append((f"pageup-site/{host}", sec, lambda h=host, emp=emp: C.pageup_site(h, emp)))
    for host, portal, emp, sec in SRC.get("elmo", []):
        t.append((f"elmo/{host}", sec, lambda h=host, po=portal, emp=emp: C.elmo(h, po, emp)))
    for site, emp, sec in SRC.get("wordpress", []):
        t.append((f"wordpress/{site.split('/')[2]}", sec, lambda si=site, emp=emp: C.wp_jobs(si, emp)))
    for listing, link_re, emp, sec, src, *pages in SRC.get("careers_site", []):
        t.append((f"{src}/{emp}", sec, lambda l=listing, r=link_re, emp=emp, src=src, mp=(pages or [15])[0]: C.listing_site(l, r, emp, src, mp)))
    for host, company, emp, sec in SRC.get("sf_classic", []):
        t.append((f"sf-classic/{company}", sec, lambda h=host, co=company, emp=emp: C.sf_classic(h, co, emp)))
    for tenant, site, emp, sec in SRC.get("cornerstone", []):
        t.append((f"cornerstone/{tenant}", sec, lambda te=tenant, si=site, emp=emp: C.cornerstone(te, si, emp)))
    for key, fn in (("vic_gov", C.vic_gov_or_cache), ("aps_gazette", C.aps_gazette), ("qld_gov", C.qld_gov), ("wa_gov", C.wa_gov)):
        if SRC.get(key):
            t.append((key.replace("_", "-"), "Government", fn))
    if SRC.get("remotive"):
        t.append(("remotive", "Remote", C.remotive))
    return t


def collect():
    """Run sources side by side (8 at a time). Each source still pauses between its own requests."""
    import concurrent.futures as cf

    def run_one(task):
        name, sector, fn = task
        got = []
        try:
            for j in fn():
                j["sector"] = sector
                got.append(j)
            return got, f"ok   {name}: {len(got)} candidates"
        except Exception as e:
            return got, f"FAIL {name}: {type(e).__name__} {str(e)[:120]}"

    raw = []
    with cf.ThreadPoolExecutor(8) as ex:
        for got, line in ex.map(run_one, tasks()):
            raw += got
            log.append(line)
    return raw


def build(raw):
    out, seen = [], set()
    for j in raw:
        title = re.sub(r"\s+", " ", j["title"]).strip()
        disc = T.discipline(title, j.get("description", ""))
        if not disc:
            continue
        # A location that is only a work mode ("Hybrid", "Remote") on an Australian employer's site.
        if re.fullmatch(r"\s*(hybrid|remote|flexible|on-?site|multiple locations)\s*", j["location"] or "", re.I) and j["source"] in ("workday", "oracle", "successfactors", "pageup", "pageup-site", "avature", "radancy", "phenom", "livehire", "sf-classic"):
            j["workplace"] = j.get("workplace") or j["location"].strip().title()
            j["location"] = ""
        # An Australian employer's own careers site with no location on the ad: assume Australia.
        if not (j["location"] or "").strip() and j["source"] in ("workday", "oracle", "successfactors", "pageup", "pageup-site", "avature", "radancy", "phenom", "livehire", "sf-classic"):
            j["location"] = "Australia"
        if j["source"] not in ("wa-gov", "vic-gov", "qld-gov") and not T.in_scope_location(j["location"], j.get("workplace", ""), j.get("description", "")):
            continue
        if j.pop("_needs_detail", False):
            try:
                time.sleep(C.DELAY)
                C.wa_gov_detail(j)
            except Exception:
                pass
        desc = j.get("description", "")
        if j.get("sector") in ("Construction", "Mining") and re.search(r"design (manager|coordinator|engineer)|design lead\b(?!.*(experience|service|human|digital))", title, re.I) \
                and not T.OVERRIDE.search(title):
            continue  # "design manager" etc. means engineering design in these industries
        # De-duplicate the same role found in two places (e.g. an agency site and the APS Gazette).
        norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
        emp_key, t_key = norm(j["employer"])[:12], norm(title)
        # Same title, or the same role listed by two different sources with one title extending the other.
        if any(e == emp_key and (t == t_key or (src != j["source"] and (t.startswith(t_key[:20]) or t_key.startswith(t[:20]))))
               for e, t, src in seen):
            continue
        seen.add((emp_key, t_key, j["source"]))
        url, link_type = C.resolve_link(j)
        if re.search(r"internalcareers|internaljobs|/internal", url, re.I):
            continue  # staff-only job boards: not open to the public
        time.sleep(0.3)
        p = T.pay(j.get("salary_text", ""), desc)
        st = T.states_of(j["location"]) or (["WA"] if j["source"] == "wa-gov" else ["VIC"] if j["source"] == "vic-gov" else ["QLD"] if j["source"] == "qld-gov" else [])
        mode = T.work_mode(j["location"], j.get("workplace", ""), desc)
        out.append(dict(
            id=hashlib.md5(j["source_id"].encode()).hexdigest()[:10],
            title=title, employer=j["employer"], sector=j.get("sector", ""),
            discipline=disc, seniority=T.seniority(title, desc),
            people_leader=T.people_leader(title, desc),
            location=j["location"] or ", ".join(st), states=st,
            remote_apac=(mode == "Remote" and not st),
            work_mode=mode, employment=T.employment(j.get("employment_type", ""), title, desc),
            pay=p, via_recruiter=T.via_recruiter(j["employer"], desc),
            posted=j.get("posted", ""), url=url, link_type=link_type, source=j["source"],
            summary=T.summary(desc),
        ))
        DESCS[out[-1]["id"]] = desc
    return out


DESCS = {}   # full ad text by role id, used for AI summaries and not published

PREVIOUS = "https://krustywan.github.io/designroles-au/jobs.json"


PREV_AI = {}   # AI summaries already on the published board


def remember_first_seen(jobs, today):
    """Give every role the date we first saw it, by reading yesterday's published board.
    Roles that were already on the board before we tracked this get their posted date (or none)."""
    prev, by_url = {}, {}
    try:
        old = json.loads(C.get(PREVIOUS, tries=2))
        for j in old.get("jobs", []):
            prev[j["id"]] = by_url[j["url"]] = j["first_seen"] if "first_seen" in j else (j.get("posted") or "")
            if j.get("ai"):
                PREV_AI[j["id"]] = j["ai"]
        log.append(f"first-seen dates: read {len(prev)} roles from the published board")
    except Exception as e:
        log.append(f"first-seen dates: could not read the published board ({e}); new roles dated today")
    for j in jobs:
        j["first_seen"] = prev.get(j["id"], by_url.get(j["url"], today))


if __name__ == "__main__":
    t0 = time.time()
    raw = collect()
    json.dump(raw, open("raw.json", "w"))
    jobs = build(raw)
    perth = time.gmtime(time.time() + 8 * 3600)  # GitHub's computers run on UTC; the board shows Perth time
    remember_first_seen(jobs, time.strftime("%Y-%m-%d", perth))
    summarise.add_summaries(jobs, DESCS, PREV_AI, log)
    jobs.sort(key=lambda x: x["posted"] or x["first_seen"] or "", reverse=True)
    json.dump(dict(generated=time.strftime("%Y-%m-%d %H:%M", perth), count=len(jobs), jobs=jobs),
              open("jobs.json", "w"), indent=1)
    print("\n".join(log))
    print(f"raw candidates: {len(raw)}  kept: {len(jobs)}  in {time.time()-t0:.0f}s")
