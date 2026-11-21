"""AI summaries of each job ad, written once per role and reused on later days.

Runs inside run.py on GitHub's computers. Needs an Anthropic API key saved as the
repository secret ANTHROPIC_API_KEY; without one, the board keeps the rule-based summaries.
Summaries only use what the ad says. Roles summarised on an earlier day are copied from the
published board, so each role is only sent once (a few cents a month at current volumes)."""
import json, os, re, urllib.request
from concurrent.futures import ThreadPoolExecutor

MODEL = os.environ.get("SUMMARY_MODEL", "claude-haiku-5-5")
MAX_NEW = int(os.environ.get("SUMMARY_MAX_NEW", "150"))   # a ceiling per run, so a bad day can't run up a bill

SYSTEM = """You summarise job ads for a job board for designers and researchers in Australia.
Use only facts stated in the ad. Never invent pay, benefits, tools, team names or requirements.
Write in plain Australian English, second person ("you'll"), no hype, no emoji.
Reply with JSON only, matching this shape exactly:
{"overview": "2 sentences, max 45 words: what the role is and where it sits in the organisation",
 "do": ["up to 4 short points on what you'll do, each max 14 words"],
 "need": ["up to 4 short points on what they're looking for, each max 14 words"],
 "perks": ["up to 3 short points on benefits or ways of working the ad mentions, each max 12 words"]}
Leave a list empty if the ad doesn't say. If the ad text is too thin to summarise, return {"overview": ""}."""


def ask(job, desc, key):
    body = {
        "model": MODEL, "max_tokens": 600, "system": SYSTEM,
        "messages": [{"role": "user", "content": f"Job title: {job['title']}\nEmployer: {job['employer']}\nLocation: {job['location']}\n\nAd:\n{desc[:12000]}"}],
    }
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                 headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = "".join(b.get("text", "") for b in json.loads(r.read()).get("content", []))
    m = re.search(r"\{.*\}", text, re.S)
    data = json.loads(m.group(0)) if m else {}
    clean = lambda xs, n: [str(x).strip() for x in (xs or []) if str(x).strip()][:n]
    out = {"overview": str(data.get("overview", "")).strip(), "do": clean(data.get("do"), 4),
           "need": clean(data.get("need"), 4), "perks": clean(data.get("perks"), 3)}
    return out if out["overview"] else None


def add_summaries(jobs, descs, previous, log):
    """jobs: board records; descs: id -> full ad text; previous: id -> earlier AI summary."""
    todo = []
    for j in jobs:
        if previous.get(j["id"]):
            j["ai"] = previous[j["id"]]
        elif len(descs.get(j["id"], "")) > 300:
            todo.append(j)
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        log.append(f"AI summaries: no API key set; {len(todo)} roles keep the rule-based summary")
        return
    todo = todo[:MAX_NEW]
    done = 0

    def one(j):
        nonlocal done
        try:
            s = ask(j, descs[j["id"]], key)
            if s:
                j["ai"] = s; done += 1
        except Exception as e:
            log.append(f"AI summary failed for {j['title'][:40]}: {str(e)[:80]}")

    with ThreadPoolExecutor(4) as ex:
        list(ex.map(one, todo))
    log.append(f"AI summaries: {done} new, {sum(1 for j in jobs if j.get('ai')) - done} reused")
