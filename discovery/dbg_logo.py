import sys; sys.path.insert(0, ".")
import fetch_logos as F
for d in ["bhp.com", "canva.com", "hcf.com.au", "macquarie.com", "bupa.com.au"]:
    try: icons = F.page_icons(d)
    except Exception as e: icons = str(e)
    print("ICONS", d, icons[:5] if isinstance(icons, list) else icons)
    for u in ([f"https://www.google.com/s2/favicons?domain={d}&sz=128", f"https://icons.duckduckgo.com/ip3/{d}.ico"] + (icons[:3] if isinstance(icons, list) else [])):
        try:
            b = F.fetch(u); print("  ", u[:80], len(b), b[:8], F.size(b))
        except Exception as e: print("  ", u[:80], "ERR", str(e)[:80])
