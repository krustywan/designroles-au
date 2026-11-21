import sys
sys.path.insert(0, ".")
import connectors as C, tagger as T
def show(name, gen):
    n = 0
    try:
        for j in gen:
            n += 1
            print("JOB", name, "|", j["employer"][:30], "|", j["title"][:60], "|", j["location"][:40], "|", T.discipline(j["title"], j["description"]), "|", T.in_scope_location(j["location"], j.get("workplace",""), j["description"]), "|", j["url"][:90], flush=True)
        print("DONE", name, n, flush=True)
    except Exception as e:
        import traceback; traceback.print_exc(); print("ERR", name, e, flush=True)
show("macquarie", C.avature("https://recruitment.macquarie.com/en_US/careers", "Macquarie Group"))
show("optus", C.listing_site("https://careers.optus.com.au/jobs?page={page}", r'/[\w-]+/job/\d+', "Optus", "optus"))
show("livehire-bcf", C.listing_site("https://www.livehire.com/careers/bcf/jobs", r'(?:https://www\.livehire\.com)?/careers/bcf/job/[\w/-]+', "BCF", "livehire"))
show("eh", C.listing_site("https://employmenthero.com/jobs/?q=designer&page={page}", r'(?:https://employmenthero\.com)?/jobs/position/[\w-]+/?', "Employment Hero", "employmenthero", 5))
