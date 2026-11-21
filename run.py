"""Run every connector, keep Australian design/research roles, tag them and write jobs.json.

Usage: python3 run.py            (all sources in sources.json)
"""
import json, time, re, sys, traceback, hashlib
import connectors as C
import tagger as T

SRC = json.load(open("sources.json"))
log = []


def collect():
    raw = []

    def take(name, gen, sector):
        n0 = len(raw)
        try:
            for j in gen:
                j["sector"] = sector
                raw.append(j)
            log.append(f"ok   {name}: {len(raw)-n0} candidates")
        except Exception as e:
            log.append(f"FAIL {name}: {type(e).__name__} {str(e)[:120]}")
        time.sleep(C.DELAY)

    for tok, emp, sec in SRC.get("greenhouse", []):
        take(f"greenhouse/{tok}", C.greenhouse(tok, emp), sec)
    for tok, emp, sec in SRC.get("lever", []):
        take(f"lever/{tok}", C.lever(tok, emp), sec)
    for tok, emp, sec in SRC.get("ashby", []):
        take(f"ashby/{tok}", C.ashby(tok, emp), sec)
    for tok, emp, sec in SRC.get("smartrecruiters", []):
        take(f"smartrecruiters/{tok}", C.smartrecruiters(tok, emp), sec)
    for pid, brand, emp, sec in SRC.get("pageup", []):
        take(f"pageup/{pid}", C.pageup(pid, brand, emp), sec)
    for host, tenant, site, emp, sec in SRC.get("workday", []):
        C.DELAY, d0 = 1.5, C.DELAY
        take(f"workday/{tenant}", C.workday(host, tenant, site, emp), sec)
        C.DELAY = d0
    for host, emp, sec, loc in SRC.get("successfactors", []):
        take(f"successfactors/{host}", C.sf_rss(host, emp, loc), sec)
    for host, emp, sec in SRC.get("radancy", []):
        take(f"radancy/{host}", C.radancy(host, emp), sec)
    for base, emp, sec in SRC.get("avature", []):
        take(f"avature/{base.split('/')[2]}", C.avature(base, emp), sec)
    if SRC.get("vic_gov"):
        take("vic-gov", C.vic_gov(), "Government")
    if SRC.get("wa_gov"):
        take("wa-gov", C.wa_gov(), "Government")
    if SRC.get("remotive"):
        take("remotive", C.remotive(), "Remote")
    return raw


def build(raw):
    out, seen = [], set()
    for j in raw:
        title = re.sub(r"\s+", " ", j["title"]).strip()
        disc = T.discipline(title, j.get("description", ""))
        if not disc:
            continue
        if j["source"] not in ("wa-gov", "vic-gov") and not T.in_scope_location(j["location"], j.get("workplace", ""), j.get("description", "")):
            continue
        if j.pop("_needs_detail", False):
            try:
                time.sleep(C.DELAY)
                C.wa_gov_detail(j)
            except Exception:
                pass
        desc = j.get("description", "")
        key = (j["employer"].lower(), title.lower(), (j["location"] or "").lower()[:20])
        if key in seen:
            continue
        seen.add(key)
        url, link_type = C.resolve_link(j)
        if re.search(r"internalcareers|internaljobs|/internal", url, re.I):
            continue  # staff-only job boards: not open to the public
        time.sleep(0.3)
        p = T.pay(j.get("salary_text", ""), desc)
        st = T.states_of(j["location"]) or (["WA"] if j["source"] == "wa-gov" else ["VIC"] if j["source"] == "vic-gov" else [])
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
    return out


if __name__ == "__main__":
    t0 = time.time()
    raw = collect()
    json.dump(raw, open("raw.json", "w"))
    jobs = build(raw)
    jobs.sort(key=lambda x: x["posted"] or "", reverse=True)
    json.dump(dict(generated=time.strftime("%Y-%m-%d %H:%M"), count=len(jobs), jobs=jobs),
              open("jobs.json", "w"), indent=1)
    print("\n".join(log))
    print(f"raw candidates: {len(raw)}  kept: {len(jobs)}  in {time.time()-t0:.0f}s")
