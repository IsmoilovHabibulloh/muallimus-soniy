#!/usr/bin/env python3
"""Asl nusxa bilan API ma'lumotlarini solishtirish."""
import urllib.request, json

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

for pn in range(36, 48):
    resp = urllib.request.urlopen(f"{API}/book/pages/{pn}")
    data = json.loads(resp.read())
    units = sorted(data.get("text_units", []), key=lambda u: u["sort_order"])
    
    print(f"\n{'='*80}")
    print(f"SAHIFA {pn} ({len(units)} unit)")
    print(f"{'='*80}")
    
    for u in units:
        sec = (u.get("metadata") or {}).get("section", "")
        text = u["text_content"][:90].replace("\n", " ")
        print(f"  [{u['sort_order']:3d}] id={u['id']:5d} {sec:30s} | {text}")
