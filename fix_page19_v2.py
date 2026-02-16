#!/usr/bin/env python3
"""Fix page 19: replace tanvin (ٌ U+064C) with sukun (ْ U+0652) in affected units."""

import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://ikkinchimuallim.codingtech.uz/api/v1"


def api_req(url, data=None, headers=None, method=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    return json.loads(urllib.request.urlopen(req, context=ctx).read())


# Login
token_resp = api_req(
    f"{BASE_URL}/admin/auth/login",
    {"username": "admin", "password": "MuallimuS2026!Adm"},
)
token = token_resp["access_token"]
print(f"Token: {token[:30]}...")
headers = {"Authorization": f"Bearer {token}"}

# Get page 19
page = api_req(f"{BASE_URL}/book/pages/19")
page_id = page["id"]
print(f"Page ID: {page_id}")
print(f"Total units: {len(page.get('text_units', []))}")

TANVIN_DAMM = "\u064C"  # ٌ dammatayn
SUKUN = "\u0652"  # ْ sukun

target_sections = [
    "lesson5_r1",
    "lesson5_r3",
    "lesson5_r4",
    "lesson5_r5",
    "lesson5_r6",
    "lesson5_r7",
    "lesson5_r8",
]

updates = []
for unit in page.get("text_units", []):
    text = unit["text_content"]
    section = unit.get("metadata", {}).get("section", "")

    if section in target_sections and TANVIN_DAMM in text:
        fixed = text.replace(TANVIN_DAMM, SUKUN)
        updates.append({"id": unit["id"], "action": "update", "text_content": fixed})
        print(f"  Fix [{section}]: {text} -> {fixed}")

print(f"\nTotal fixes: {len(updates)}")

if updates:
    result = api_req(
        f"{BASE_URL}/admin/book/pages/{page_id}/units/bulk",
        updates,
        headers,
        method="PUT",
    )
    print(f"Result: {result}")
else:
    print("No updates needed!")
