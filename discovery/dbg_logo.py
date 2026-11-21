import sys, json, re; sys.path.insert(0, ".")
import fetch_logos as F
for d in ["hcf.com.au", "bupa.com.au", "wesfarmers.com.au", "atari.com", "anglicarewa.org.au", "lagardere-tr.com", "naa.gov.au", "nhvr.gov.au", "niaa.gov.au", "ramint.gov.au", "acer.org"]:
    for u in [f"https://unavatar.io/{d}?fallback=false", f"https://www.google.com/s2/favicons?domain_url=https://www.{d}/&sz=256",
              f"https://{d}/favicon.ico", f"https://www.{d}/favicon.ico", f"https://www.{d}/manifest.json", f"https://www.{d}/site.webmanifest",
              f"https://en.wikipedia.org/w/api.php?action=query&titles={d}&format=json"]:
        try:
            b = F.fetch(u); k = F.kind_and_size(b)
            extra = ""
            if "manifest" in u or "webmanifest" in u:
                try: extra = str([i.get("src") + " " + i.get("sizes", "") for i in json.loads(b).get("icons", [])][:4])
                except Exception: extra = "notjson"
            print("L", d, u[:70], len(b), k, extra[:150])
        except Exception as e:
            print("L", d, u[:70], "ERR", str(e)[:60])
