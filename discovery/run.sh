#!/usr/bin/env bash
pip -q install pillow cairosvg
python3 - <<'PY'
import re, io, os, json, urllib.request, urllib.parse
from PIL import Image
import cairosvg
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
get=lambda u: urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read()
os.makedirs("discovery/out/x",exist_ok=True); n=0
def save(tag,b):
    global n
    try:
        if b"<svg" in b[:3000]: b=cairosvg.svg2png(bytestring=b,output_width=600)
        im=Image.open(io.BytesIO(b)); im.load(); n+=1; im.convert("RGBA").save(f"discovery/out/x/{n:02d}_{tag}.png"); print("SAVED",n,tag,im.size)
    except Exception as e: print("ERR",tag,e)
for q in ["Michael Hill logo","Coates Hire logo","Coates logo"]:
    try:
        r=json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","list":"search","srsearch":q,"srnamespace":6,"format":"json","srlimit":5})))
        for h in r["query"]["search"]:
            t=h["title"]; print("COMMONS",q,"|",t)
            if re.search(r"michael.?hill|coates",t,re.I): save("commons-"+re.sub(r"\W+","",t)[:20], get("https://commons.wikimedia.org/wiki/Special:FilePath/"+urllib.parse.quote(t.replace("File:","").replace(" ","_"))+"?width=600"))
    except Exception as e: print("ERR commons",e)
for dom in ["https://www.coates.com.au/","https://www.michaelhill.com.au/"]:
    try:
        h=get(dom).decode("utf8","ignore")
        for m in re.finditer(r'<svg[^>]*>.*?</svg>',h,re.S):
            ctx=h[max(0,m.start()-400):m.start()]
            if re.search(r'logo|brand|home',ctx,re.I): save("inline-"+dom[12:20], m.group(0).encode())
        for u in re.findall(r'(?:src|href|data-src)="([^"]+\.(?:svg|png))"',h):
            if re.search(r'logo',u,re.I): save("file-"+dom[12:20], get(urllib.parse.urljoin(dom,u)))
    except Exception as e: print("ERR",dom,e)
PY
