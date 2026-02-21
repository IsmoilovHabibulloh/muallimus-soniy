#!/usr/bin/env python3
"""Fix sort_order gaps on kalima pages 34-35."""
import urllib.request
import json

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

# Login
login_data = json.dumps({"username":"admin","password":"MuallimuS2026!Adm"}).encode()
req = urllib.request.Request(f"{API}/admin/auth/login", data=login_data, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req)
token = json.loads(resp.read())["access_token"]

for pn in [34, 35]:
    resp = urllib.request.urlopen(f"{API}/book/pages/{pn}")
    data = json.loads(resp.read())
    page_id = data["id"]
    units = sorted(data.get("text_units", []), key=lambda u: u["sort_order"])
    
    print(f"\nSAHIFA {pn} (page_id={page_id})")
    
    # Build bulk update to fix sort_orders
    bulk = []
    for i, u in enumerate(units):
        if u["sort_order"] != i:
            print(f"  FIX: id={u['id']} sort_order {u['sort_order']} -> {i}")
            bulk.append({
                "action": "update",
                "id": u["id"],
                "sort_order": i
            })
        else:
            print(f"  OK:  id={u['id']} sort_order={i}")
    
    if bulk:
        bulk_data = json.dumps(bulk).encode()
        req2 = urllib.request.Request(
            f"{API}/admin/book/pages/{page_id}/units/bulk",
            data=bulk_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            method="PUT"
        )
        r2 = urllib.request.urlopen(req2)
        print(f"  RESULT: {r2.status} - {r2.read().decode()[:200]}")
    else:
        print("  No changes needed")
