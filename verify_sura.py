#!/usr/bin/env python3
import requests, re

API = "https://ikkinchimuallim.codingtech.uz/api/v1"
marker = re.compile(r'﴿[٠-٩]+﴾')

issues = 0
for pn in range(36, 48):
    r = requests.get(f"{API}/book/pages/{pn}")
    data = r.json()
    units = data["text_units"]
    ayat_units = [u for u in units if "_ayat" in ((u.get("metadata") or {}).get("section", ""))]
    
    bad = []
    for u in ayat_units:
        markers = marker.findall(u["text_content"])
        if len(markers) != 1:
            bad.append(f"  unit {u['id']}: {len(markers)} markers")
            issues += 1
    
    status = f"❌ {len(bad)} issues" if bad else "✅"
    print(f"Page {pn}: {len(ayat_units)} ayat units {status}")
    for b in bad:
        print(b)

print(f"\nTotal issues: {issues}")
