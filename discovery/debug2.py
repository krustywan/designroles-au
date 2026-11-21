import sys, re
sys.path.insert(0, ".")
import connectors as C
for h in ["careers.originenergy.com.au", "careers.woodside.com.au", "careers.colesgroup.com.au"]:
    b = C.get(f"https://{h}/services/rss/job/?locale=en_US&keywords=designer").decode("utf8", "ignore")
    print("SF", h, b.count("<item>"), re.findall(r"<title>([^<]{0,70})", b)[:8], flush=True)
