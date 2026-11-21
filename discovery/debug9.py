import sys, json
sys.path.insert(0, ".")
import connectors as C
for site in ["https://bluefinresources.com.au", "https://hudson.com", "https://www.talentweb.com.au", "https://theonset.com.au",
             "https://talentnation.com.au", "https://clicks.com.au", "https://www.igniteco.com", "https://launchrecruitment.com.au"]:
    try:
        d = json.loads(C.get(site + "/wp-json/", tries=1))
        routes = [r for r in d.get("routes", {}) if any(w in r.lower() for w in ("job", "vacanc", "listing", "position"))][:8]
        print("WP", site, routes, flush=True)
        for r in routes:
            if "(?P" in r or not r.startswith("/wp/v2/"):
                continue
            try:
                items = json.loads(C.get(site + "/wp-json" + r + "?per_page=5", tries=1))
                if isinstance(items, list):
                    print("   ", r, len(items), [((i.get("title") or {}).get("rendered") if isinstance(i.get("title"), dict) else i.get("name")) for i in items[:3]], flush=True)
            except Exception as e:
                print("   ", r, "ERR", str(e)[:60])
    except Exception as e:
        print("WP", site, "ERR", str(e)[:80], flush=True)
