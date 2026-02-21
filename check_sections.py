#!/usr/bin/env python3
"""Check actual unit_type values for page 34 units."""
import urllib.request
import json

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

resp = urllib.request.urlopen(f"{API}/book/pages/34")
data = json.loads(resp.read())

print("=== PAGE 34 FULL UNIT DATA ===")
for u in sorted(data.get("text_units", []), key=lambda x: x["sort_order"]):
    print(f"  sort={u['sort_order']} unit_type='{u.get('unit_type','')}' section='{u.get('metadata_',{}).get('section','')}' text='{u['text_content'][:60]}'")
    print(f"    metadata_keys: {list((u.get('metadata_',{}) or {}).keys())}")
    print(f"    full_metadata: {json.dumps(u.get('metadata_',{}), ensure_ascii=False)[:200]}")
