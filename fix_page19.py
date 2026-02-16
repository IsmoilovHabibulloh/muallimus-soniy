#!/usr/bin/env python3
"""Fix page 19: replace tanvin (ٌ) with sukun (ْ) in affected units."""

import urllib.request
import json

BASE_URL = "https://ikkinchimuallim.codingtech.uz/api/v1"

def api_post(url, data, headers=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers or {})
    req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def api_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def api_put(url, data, headers=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers or {}, method="PUT")
    req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# Login
token_resp = api_post(f"{BASE_URL}/admin/auth/login", {
    "username": "admin", "password": "admin123"
})
token = token_resp.get("access_token")
print(f"Token: {token[:20]}...")
headers = {"Authorization": f"Bearer {token}"}

# Get page 19
page = api_get(f"{BASE_URL}/book/pages/19")
page_id = page["id"]
print(f"Page ID: {page_id}")

TANVIN = '\u064C'  # ٌ (dammatayn)
SUKUN = '\u0652'    # ْ  

target_sections = [
    "lesson5_r1", "lesson5_r3", "lesson5_r4",
    "lesson5_r5", "lesson5_r6", "lesson5_r7", "lesson5_r8"
]

updates = []
for unit in page.get("text_units", []):
    text = unit["text_content"]
    section = unit.get("metadata", {}).get("section", "")
    
    if section in target_sections and TANVIN in text:
        fixed = text.replace(TANVIN, SUKUN)
        updates.append({"id": unit["id"], "action": "update", "text_content": fixed})
        print(f"  Unit {unit['id']}: '{text}' → '{fixed}'")

print(f"\nTotal: {len(updates)} updates")

if updates:
    result = api_put(f"{BASE_URL}/admin/book/pages/{page_id}/units/bulk", updates, headers)
    print(f"Result: {result}")
