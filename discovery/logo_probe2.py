import re, urllib.request, os, io
from PIL import Image
import cairosvg
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
os.makedirs("discovery/out/x", exist_ok=True)
h = get("https://www.wesfarmers.com.au/").decode("utf8", "ignore")
print("LEN", len(h))
for m in re.finditer(r'(<img[^>]{0,300}>|<svg[^>]{0,200}>|<a[^>]+class="[^"]*logo[^"]*"[^>]*>|src="[^"]+"|href="[^"]+\.(?:svg|png|ico)[^"]*")', h):
    print("TAG", m.group(0)[:250])
for i, u in enumerate(["https://web.archive.org/web/2025id_/https://www.naa.gov.au/themes/custom/custom/naa/logo.png",
                       "https://web.archive.org/web/2024id_/https://www.naa.gov.au/themes/custom/custom/naa/logo.svg",
                       "https://www.wesfarmers.com.au/favicon.ico"]):
    try:
        b = get(u); print("GOT", u, len(b), b[:12])
        if b"<svg" in b[:3000]: b = cairosvg.svg2png(bytestring=b, output_width=512)
        im = Image.open(io.BytesIO(b)); im.load(); print("SIZE", u, im.size, getattr(im, "info", {}).get("sizes"))
        if hasattr(im, "ico"): im = im.ico.getimage(max(im.ico.sizes()))
        im.convert("RGBA").save(f"discovery/out/x/{i}.png")
    except Exception as e: print("ERR", u, e)
