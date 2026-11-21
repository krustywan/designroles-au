import sys, re
sys.path.insert(0, ".")
import connectors as C
for u in ["https://anglicarewa.elmotalent.com.au/careers/default", "https://anglicarewa.elmotalent.com.au/careers/default/rss",
          "https://anglicarewa.elmotalent.com.au/careers/default/jobs/rss", "https://anglicarewa.elmotalent.com.au/careers/default/job/view/931",
          "https://beachamgroup.com/latest-jobs/"]:
    try:
        b = C.get(u, tries=1).decode("utf8", "ignore")
        print("URL", u, len(b), "| items", b.count("<item>"), "| ld", "JobPosting" in b,
              "|", re.findall(r'href="[^"]*(?:rss|feed|xml)[^"]*"|jobadder[^"\' ]{0,60}|/job/view/\d+|<title>[^<]{0,60}|api[./][^"\' ]{0,60}', b, re.I)[:12], flush=True)
    except Exception as e:
        print("URL", u, "ERR", e, flush=True)
for j in C.workday("perthairport.wd105.myworkdayjobs.com", "perthairport", "PerthAirport", "Perth Airport"):
    print("WD", j["title"], "|", j["location"])
