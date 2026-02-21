#!/usr/bin/env python3
"""Fix sort_order gaps on pages 34-35 — normalize to 0,1,2,...,N"""
import urllib.request
import json

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

def api_post(url, data, headers=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers or {})
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def api_get(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())

def api_put(url, data, headers):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="PUT")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

# Get token
r = api_post(f"{API}/admin/auth/login", {"username":"admin","password":"MuallimuS2026!Adm"})
token = r["access_token"]
headers = {"Authorization": f"Bearer {token}"}

for page_num in [34, 35]:
    print(f"\n{'='*50}")
    print(f"Page {page_num}")
    print(f"{'='*50}")
    
    page_data = api_get(f"{API}/book/pages/{page_num}")
    page_id = page_data["id"]
    units = page_data["text_units"]
    
    current_orders = [u["sort_order"] for u in units]
    expected_orders = list(range(len(units)))
    
    print(f"  Page ID: {page_id}")
    print(f"  Units: {len(units)}")
    print(f"  Current sort_orders: {current_orders}")
    print(f"  Expected sort_orders: {expected_orders}")
    
    if current_orders == expected_orders:
        print(f"  ✅ Already normalized, skipping.")
        continue
    
    updates = []
    for i, unit in enumerate(units):
        if unit["sort_order"] != i:
            updates.append({
                "action": "update",
                "id": unit["id"],
                "sort_order": i,
            })
            sec = unit['metadata'].get('section','')
            print(f"  Fix: id={unit['id']} sort_order {unit['sort_order']} → {i} ({sec})")
    
    if updates:
        result = api_put(f"{API}/admin/book/pages/{page_id}/units/bulk", updates, headers)
        print(f"  Result: {result}")
    else:
        print(f"  No updates needed.")

print("\n✅ Sort orders normalized!")
