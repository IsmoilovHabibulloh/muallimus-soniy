#!/usr/bin/env python3
"""Check sort_order issues on all sura pages."""
import requests

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

for pn in range(36, 48):
    data = requests.get(f"{API}/book/pages/{pn}").json()
    units = sorted(data.get("text_units", []), key=lambda u: u["sort_order"])
    
    suras_on_page = {}
    for u in units:
        sec = (u.get("metadata") or {}).get("section", "")
        sura_name = None
        if sec.startswith("surah_") and sec.endswith("_title"):
            sura_name = sec.replace("surah_", "").replace("_title", "")
            item_type = "title"
        elif sec.startswith("bismillah_"):
            sura_name = sec.replace("bismillah_", "")
            item_type = "bismillah"
        elif "_ayat" in sec:
            sura_name = sec.replace("_ayat", "").replace("_cont", "")
            item_type = "ayat"
        else:
            continue
        
        if sura_name not in suras_on_page:
            suras_on_page[sura_name] = {"title": None, "bismillah": None, "first_ayat": None, "last_ayat": None}
        
        if item_type == "title":
            suras_on_page[sura_name]["title"] = u["sort_order"]
        elif item_type == "bismillah":
            suras_on_page[sura_name]["bismillah"] = u["sort_order"]
        elif item_type == "ayat":
            if suras_on_page[sura_name]["first_ayat"] is None:
                suras_on_page[sura_name]["first_ayat"] = u["sort_order"]
            suras_on_page[sura_name]["last_ayat"] = u["sort_order"]
    
    issues = []
    sura_list = sorted(suras_on_page.items(), key=lambda x: min(v for v in x[1].values() if v is not None))
    
    for i, (sura_name, info) in enumerate(sura_list):
        title_s = info["title"]
        bismi_s = info["bismillah"]
        first_a = info["first_ayat"]
        last_a = info["last_ayat"]
        
        if title_s is not None and bismi_s is not None and first_a is not None:
            if not (title_s < bismi_s < first_a):
                issues.append(f"  X {sura_name}: title={title_s} bismi={bismi_s} ayat={first_a}-{last_a} (TARTIB XATO!)")
        
        if i > 0:
            prev_name, prev_info = sura_list[i-1]
            prev_last = prev_info.get("last_ayat")
            if prev_last is not None and title_s is not None:
                if prev_last > title_s:
                    issues.append(f"  X {prev_name} oyatlari (sort={prev_last}) > {sura_name} sarlavhasi (sort={title_s})")
    
    if issues:
        print(f"Page {pn}: MUAMMO")
        for issue in issues:
            print(issue)
    else:
        print(f"Page {pn}: OK")
