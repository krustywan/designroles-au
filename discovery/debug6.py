import sys, re, json
sys.path.insert(0, ".")
import connectors as C
for j in C.elmo("anglicarewa.elmotalent.com.au", "default", "Anglicare WA"):
    print("ELMO", j["title"], "|", j["location"], "|", j["employment_type"], "|", len(j["description"]), "|", j["description"][:120].replace("\n", " "))
for u in ["https://api.refari.co/api/v1/jobs/?key=TuFEK6zvFjI9Ot0Q6KgY0w", "https://app.refari.co/api/v1/jobs/?key=TuFEK6zvFjI9Ot0Q6KgY0w",
          "https://api.refari.co/v1/jobs?key=TuFEK6zvFjI9Ot0Q6KgY0w", "https://beachamgroup.com/wp-json/"]:
    try:
        b = C.get(u, tries=1).decode("utf8", "ignore")
        print("REF", u, len(b), b[:300].replace("\n", " "))
    except Exception as e:
        print("REF", u, "ERR", e)
