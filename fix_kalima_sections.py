#!/usr/bin/env python3
"""Add section metadata to kalima pages 34-35 units via bulk_update API."""
import urllib.request
import json

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

# Login
login_data = json.dumps({"username":"admin","password":"MuallimuS2026!Adm"}).encode()
req = urllib.request.Request(f"{API}/admin/auth/login", data=login_data, headers={"Content-Type": "application/json"})
token = json.loads(urllib.request.urlopen(req).read())["access_token"]
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

# Page 34 section mapping (by sort_order)
page34_sections = {
    0: "title_kalimat_iman",
    1: "kalima_tayyiba_title",
    2: "kalima_tayyiba",
    3: "kalima_shahada_title",
    4: "kalima_shahada",
    5: "kalima_tawhid_title",
    6: "kalima_tawhid",
    7: "kalima_radd_title",
    8: "kalima_radd",
    9: "kalima_istighfar_title",
    10: "kalima_istighfar",
}

# Page 35 section mapping (by sort_order)
# 0: istighfar continuation from page 34
# 1: كَلِمَةُ التَّمْجِيد (tamjid title)
# 2: سُبْحَانَ اللّٰهِ... (tamjid text)
# 3: مَا شَاءَ اللّٰهُ... (mashiatullah)
# 4: الْإِيمَان (iman tarif title)
# 5: إِقْرَارٌ... (iman tarif text)
# 6: إِيمَان مُجْمَل (iman mujmal title) 
# 7: آمَنْتُ بِاللّٰهِ كَمَا... (iman mujmal text)
# 8: إِيمَان مُفَصَّل (iman mufassal title)
# 9: آمَنْتُ بِاللّٰهِ وَمَلَائِكَتِهِ... (iman mufassal text)
page35_sections = {
    0: "kalima_istighfar",
    1: "kalima_tamjid_title",
    2: "kalima_tamjid",
    3: "mashiatullah",
    4: "iman_tarif_title",
    5: "iman_tarif",
    6: "iman_mujmal_title",
    7: "iman_mujmal",
    8: "iman_mufassal_title",
    9: "iman_mufassal",
}

for pn, section_map in [(34, page34_sections), (35, page35_sections)]:
    resp = urllib.request.urlopen(f"{API}/book/pages/{pn}")
    data = json.loads(resp.read())
    page_id = data["id"]
    units = sorted(data.get("text_units", []), key=lambda u: u["sort_order"])
    
    print(f"\nSAHIFA {pn} (page_id={page_id}, {len(units)} units)")
    
    bulk = []
    for i, u in enumerate(units):
        sec = section_map.get(i, "")
        if sec:
            print(f"  SET: id={u['id']} sort={i} section='{sec}' text='{u['text_content'][:40]}'")
            bulk.append({
                "action": "update",
                "id": u["id"],
                "metadata_": {"section": sec}
            })
    
    if bulk:
        bulk_data = json.dumps(bulk).encode()
        req2 = urllib.request.Request(
            f"{API}/admin/book/pages/{page_id}/units/bulk",
            data=bulk_data, headers=headers, method="PUT"
        )
        r2 = urllib.request.urlopen(req2)
        print(f"  RESULT: {r2.status} - {r2.read().decode()[:200]}")
