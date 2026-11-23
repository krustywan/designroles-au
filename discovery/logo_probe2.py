import re, urllib.request, urllib.parse, os, io
from PIL import Image
import cairosvg
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
os.makedirs("discovery/out/x", exist_ok=True)
B = "https://www.wesfarmers.com.au"
h = get(B + "/").decode("utf8", "ignore")
urls = []
for m in re.finditer(r'<link[^>]+href="([^"]+\.css[^"]*)"', h): 
    css_u = urllib.parse.urljoin(B + "/", m.group(1).replace("&amp;", "&")); print("CSS", css_u)
    try:
        css = get(css_u).decode("utf8", "ignore")
        for u in re.findall(r'url\(([^)]+)\)', css):
            u = u.strip("'\"")
            if re.search(r"logo|brand|wes", u, re.I): urls.append(urllib.parse.urljoin(css_u, u)); print("CSSURL", u)
    except Exception as e: print("ERR css", e)
i = re.search(r'class="[^"]*(?:logo|brand)[^"]*"[^>]*>(.{0,600})', h, re.S)
print("LOGOCTX", (i.group(0)[:700] if i else None))
urls += [B + "/ResourcePackages/Wesfarmers/assets/dist/img/favicon.ico", B + "/ResourcePackages/Wesfarmers/assets/dist/img/logo.svg", B + "/ResourcePackages/Wesfarmers/assets/dist/img/logo.png",
         B + "/ResourcePackages/Wesfarmers/assets/dist/img/wesfarmers-logo.svg"]
for n, u in enumerate(dict.fromkeys(urls)):
    try:
        b = get(u); print("GOT", u, len(b), b[:10])
        if b"<svg" in b[:3000]:
            open(f"discovery/out/x/w{n}.svg", "wb").write(b); b = cairosvg.svg2png(bytestring=b, output_width=600)
        im = Image.open(io.BytesIO(b)); im.load()
        if im.format == "ICO": im = im.ico.getimage(max(im.ico.sizes()))
        print("SIZE", u, im.size); im.convert("RGBA").save(f"discovery/out/x/w{n}.png")
    except Exception as e: print("ERR", u, e)
b = get("https://web.archive.org/web/2025id_/https://www.naa.gov.au/themes/custom/custom/naa/logo.png"); open("discovery/out/x/naa.png", "wb").write(b)
