#!/usr/bin/env bash
pip -q install pillow cairosvg
mkdir -p discovery/out/h
python3 - <<'PY'
import re, io, urllib.request, urllib.parse
from PIL import Image
import cairosvg
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
get=lambda u: urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
def save(name,b):
    if b"<svg" in b[:3000]: b=cairosvg.svg2png(bytestring=b,output_width=800)
    im=Image.open(io.BytesIO(b)); im.load(); im.convert("RGBA").save(f"discovery/out/h/{name}.png"); print("SAVED",name,im.size)
for name,u in [("nhvr1","https://web.archive.org/web/2025id_/https://www.nhvr.gov.au/themes/nhvr_theme/images/nhvr-logo-no-tag-navy.png")]:
    try: save(name,get(u))
    except Exception as e: print("ERR",name,e)
for site in ["https://www.hcf.com.au/","https://web.archive.org/web/2025id_/https://www.hcf.com.au/"]:
    try:
        h=get(site).decode("utf8","ignore"); print("HCF page", site, len(h))
        i=0
        for m in re.finditer(r'<img[^>]+>',h):
            if re.search(r'logo',m.group(0),re.I):
                src=re.search(r'src="([^"]+)"',m.group(0))
                if src:
                    u=urllib.parse.urljoin(site,src.group(1)); i+=1; print("HCFIMG",u)
                    try: save(f"hcf{i}",get(u))
                    except Exception as e: print("ERR",u,e)
        for m in re.finditer(r'<svg[^>]*>.*?</svg>',h,re.S):
            ctx=h[max(0,m.start()-300):m.start()]
            if re.search(r'logo',ctx+m.group(0)[:300],re.I) and len(m.group(0))>300:
                i+=1
                try: save(f"hcfsvg{i}",m.group(0).encode())
                except Exception as e: print("ERR svg",e)
        if i: break
    except Exception as e: print("ERR",site,e)
PY
