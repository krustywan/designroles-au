import json
jobs = json.load(open("jobs.json")); jobs = jobs.get("jobs", jobs) if isinstance(jobs, dict) else jobs
print("TOTAL", len(jobs))
ids = ["4544","R_371909","R_371915","544383","1370597666","1370594966","120428","121400","121396","689222","1005388","10163543","1370453266","JR104415","JR104630","JR102224","d66f2f15","241319","communication-design-assistant","423828","V-10398","6527","74070","11593","business-and-ux-analyst","226728009","1283390","JR_054450","merchantwise","/3258","42008","746","0154941","REQ267338","1440","5876","9840711","R00342055","1377332757","1438243633","1444","9QWP48NWPF","0J2IIJ1JGX","YVIUIEI334","184669892","envato"]
for i in ids:
    hit = [j for j in jobs if i.lower() in (j["url"] + j.get("apply_url","")).lower()]
    print("ID", i, "|", (hit[0]["employer"][:28] + " | " + hit[0]["title"][:50] + " | " + str(hit[0].get("discipline"))) if hit else "MISSING")
