#!/usr/bin/env python3
"""Fix 2 orphan fragments that span across pages."""
import requests

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

# Get token
r = requests.post(f"{API}/admin/auth/login", json={"username":"admin","password":"MuallimuS2026!Adm"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Fix 1: Page 37 unit 12425 "وَأَمَّا" → prepend to page 38 unit 12451
# Get page 38 unit 12451
r38 = requests.get(f"{API}/book/pages/38").json()
unit_12451 = next(u for u in r38["text_units"] if u["id"] == 12451)
new_text_38 = "وَأَمَّا " + unit_12451["text_content"]
print(f"Fix 1: Page 37 unit 12425 → prepend to page 38 unit 12451")
print(f"  Old: {unit_12451['text_content']}")
print(f"  New: {new_text_38}")

# Page 37 page_id
r37 = requests.get(f"{API}/book/pages/37").json()
page37_id = r37["id"]

# Page 38 page_id
page38_id = r38["id"]

# Delete 12425 from page 37
result1 = requests.put(f"{API}/admin/book/pages/{page37_id}/units/bulk", headers=headers,
    json=[{"action": "delete", "id": 12425}])
print(f"  Delete 12425: {result1.json()}")

# Update 12451 on page 38
result2 = requests.put(f"{API}/admin/book/pages/{page38_id}/units/bulk", headers=headers,
    json=[{"action": "update", "id": 12451, "text_content": new_text_38}])
print(f"  Update 12451: {result2.json()}")

# Fix 2: Page 46 unit 12584 "لَمْ يَلِدْ" → prepend to page 47 unit 12604
r47 = requests.get(f"{API}/book/pages/47").json()
unit_12604 = next(u for u in r47["text_units"] if u["id"] == 12604)
new_text_47 = "لَمْ يَلِدْ " + unit_12604["text_content"]
print(f"\nFix 2: Page 46 unit 12584 → prepend to page 47 unit 12604")
print(f"  Old: {unit_12604['text_content']}")
print(f"  New: {new_text_47}")

# Page 46 page_id
r46 = requests.get(f"{API}/book/pages/46").json()
page46_id = r46["id"]

# Page 47 page_id
page47_id = r47["id"]

# Delete 12584 from page 46
result3 = requests.put(f"{API}/admin/book/pages/{page46_id}/units/bulk", headers=headers,
    json=[{"action": "delete", "id": 12584}])
print(f"  Delete 12584: {result3.json()}")

# Update 12604 on page 47
result4 = requests.put(f"{API}/admin/book/pages/{page47_id}/units/bulk", headers=headers,
    json=[{"action": "update", "id": 12604, "text_content": new_text_47}])
print(f"  Update 12604: {result4.json()}")

print("\n✅ Both orphan fragments fixed!")
