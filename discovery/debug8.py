import sys
sys.path.insert(0, ".")
import connectors as C, tagger as T
for name, gen in [("beacham", C.wp_jobs("https://beachamgroup.com", "Beacham Group (recruiter)")),
                  ("elmo", C.elmo("anglicarewa.elmotalent.com.au", "default", "Anglicare WA")),
                  ("perth", C.workday("perthairport.wd105.myworkdayjobs.com", "perthairport", "PerthAirport", "Perth Airport"))]:
    for j in gen:
        print("JOB", name, "|", j["title"], "|", j["location"], "|", T.discipline(j["title"], j["description"]), "|",
              T.in_scope_location(j["location"], "", j["description"]), "|", j["url"][:90], flush=True)
