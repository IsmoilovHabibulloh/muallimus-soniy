#!/usr/bin/env python3
"""Debug: check both APIs for page 41 (Bayyina)."""
import requests, json

API = "https://ikkinchimuallim.codingtech.uz/api/v1"
r = requests.post(f"{API}/admin/auth/login", json={"username":"admin","password":"MuallimuS2026!Adm"})
token = r.json()["access_token"]

# Try admin draft API
print("=== Admin Draft API (page_id=604) ===")
draft = requests.get(f"{API}/admin/book/pages/604/draft", headers={"Authorization": f"Bearer {token}"}).json()
print(f"Keys: {list(draft.keys())}")
print(f"units count: {len(draft.get('units', []))}")
print(f"text_units count: {len(draft.get('text_units', []))}")
print()

# Try public page API  
print("=== Public Page API (page_number=41) ===")
pub = requests.get(f"{API}/book/pages/41").json()
print(f"Keys: {list(pub.keys())}")
print(f"text_units count: {len(pub.get('text_units', []))}")
if pub.get("text_units"):
    u = pub["text_units"][0]
    print(f"Unit keys: {list(u.keys())}")
    print(json.dumps(u, ensure_ascii=False))
