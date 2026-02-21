#!/usr/bin/env python3
"""Revert sort_orders on pages 34-35 back to original values."""
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

# Original sort_orders before my changes:
# Page 34: [0, 1, 2, 3, 4, 5, 6, 9, 10, 12, 13]
#   id=12207 was sort=9, I changed to 7 → revert to 9
#   id=12208 was sort=10, I changed to 8 → revert to 10
#   id=12210 was sort=12, I changed to 9 → revert to 12
#   id=12211 was sort=13, I changed to 10 → revert to 13

# Page 35: [0, 2, 3, 5, 6, 7, 9, 10, 12, 13]
#   id=12215 was sort=2, I changed to 1 → revert to 2
#   id=12216 was sort=3, I changed to 2 → revert to 3
#   id=12218 was sort=5, I changed to 3 → revert to 5
#   id=12219 was sort=6, I changed to 4 → revert to 6
#   id=12220 was sort=7, I changed to 5 → revert to 7
#   id=12222 was sort=9, I changed to 6 → revert to 9
#   id=12223 was sort=10, I changed to 7 → revert to 10
#   id=12225 was sort=12, I changed to 8 → revert to 12
#   id=12226 was sort=13, I changed to 9 → revert to 13

# Page 34 revert
page34_data = api_get(f"{API}/book/pages/34")
page34_id = page34_data["id"]

revert_34 = [
    {"action": "update", "id": 12207, "sort_order": 9},
    {"action": "update", "id": 12208, "sort_order": 10},
    {"action": "update", "id": 12210, "sort_order": 12},
    {"action": "update", "id": 12211, "sort_order": 13},
]
print("Reverting Page 34...")
result = api_put(f"{API}/admin/book/pages/{page34_id}/units/bulk", revert_34, headers)
print(f"  Result: {result}")

# Page 35 revert
page35_data = api_get(f"{API}/book/pages/35")
page35_id = page35_data["id"]

revert_35 = [
    {"action": "update", "id": 12215, "sort_order": 2},
    {"action": "update", "id": 12216, "sort_order": 3},
    {"action": "update", "id": 12218, "sort_order": 5},
    {"action": "update", "id": 12219, "sort_order": 6},
    {"action": "update", "id": 12220, "sort_order": 7},
    {"action": "update", "id": 12222, "sort_order": 9},
    {"action": "update", "id": 12223, "sort_order": 10},
    {"action": "update", "id": 12225, "sort_order": 12},
    {"action": "update", "id": 12226, "sort_order": 13},
]
print("Reverting Page 35...")
result = api_put(f"{API}/admin/book/pages/{page35_id}/units/bulk", revert_35, headers)
print(f"  Result: {result}")

# Verify
print("\n--- Verification ---")
for pn in [34, 35]:
    data = api_get(f"{API}/book/pages/{pn}")
    orders = [u["sort_order"] for u in data["text_units"]]
    print(f"Page {pn} sort_orders: {orders}")

print("\n✅ Reverted to original state!")
