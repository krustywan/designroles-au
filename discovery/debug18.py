import sys
sys.path.insert(0, ".")
import connectors as C, tagger as T
for name, fn in [("raa", lambda: C.listing_site("https://jobs.silkroad.com/RAA/RAACareers?page={page}", r"(?:https://jobs\.silkroad\.com)?/RAA/RAACareers/jobs/\d+", "RAA", "silkroad")), ("breville", lambda: C.cornerstone("brevillesage",1,"Breville"))]:
    for j in fn(): print("T", name, "|", j["title"], "|", j["location"], "|", T.discipline(j["title"], j["description"]), "|", j["url"])
