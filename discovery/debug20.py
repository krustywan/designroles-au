import sys, re, urllib.parse
sys.path.insert(0, ".")
import connectors as C
for kw in ["Consultant", "design", "experience"]:
    raw = C.get("https://www.jobs.global.fujitsu.com/services/rss/job/?" + urllib.parse.urlencode({"locale": "en_US", "keywords": kw})).decode("utf8","ignore")
    for item in re.findall(r"<item>(.*?)</item>", raw, re.S):
        if "11593" in item:
            print("FJITEM", kw, C.strip_html(item.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&"))[:4000].replace("\n"," "))
            raise SystemExit
print("FJ not found")
