#!/usr/bin/env python3
"""
Fix sort_order on sura pages so each sura's content is contiguous:
  title -> bismillah -> ayats -> next sura title -> ...

Usage:
  python fix_sort_order.py --dry-run   # Preview
  python fix_sort_order.py             # Apply
"""

import argparse
import requests

API = "https://ikkinchimuallim.codingtech.uz/api/v1"
ADMIN_USER = "admin"
ADMIN_PASS = "MuallimuS2026!Adm"


def get_token():
    r = requests.post(f"{API}/admin/auth/login", json={
        "username": ADMIN_USER, "password": ADMIN_PASS,
    })
    r.raise_for_status()
    return r.json()["access_token"]


def get_page_data(page_number):
    r = requests.get(f"{API}/book/pages/{page_number}")
    r.raise_for_status()
    return r.json()


def bulk_update(token, page_id, actions):
    r = requests.put(
        f"{API}/admin/book/pages/{page_id}/units/bulk",
        headers={"Authorization": f"Bearer {token}"},
        json=actions,
    )
    r.raise_for_status()
    return r.json()


def get_sura_name_from_section(section):
    """Extract sura name and type from section string."""
    if section.startswith("surah_") and section.endswith("_title"):
        return section.replace("surah_", "").replace("_title", ""), "title"
    elif section.startswith("bismillah_"):
        return section.replace("bismillah_", ""), "bismillah"
    elif "_ayat" in section:
        name = section.replace("_ayat", "").replace("_cont", "")
        return name, "ayat"
    elif section == "istiaza":
        return None, "istiaza"
    else:
        return None, "other"


def reorder_page(units):
    """
    Reorder units so each sura's content is contiguous:
    [istiaza] [sura1_title, sura1_bismillah, sura1_ayats...] [sura2_title, ...]
    
    Returns list of (unit_id, new_sort_order) tuples, or empty if already correct.
    """
    # Step 1: Find the order of suras by their title's sort_order
    sura_order = []  # list of sura names in order they appear
    sura_groups = {}  # sura_name -> {title: unit, bismillah: unit, ayats: [units]}
    prefix_units = []  # istiaza, etc.
    
    for u in units:
        sec = (u.get("metadata") or {}).get("section", "")
        sura_name, item_type = get_sura_name_from_section(sec)
        
        if item_type in ("istiaza", "other"):
            prefix_units.append(u)
            continue
        
        if sura_name not in sura_groups:
            sura_groups[sura_name] = {"title": None, "bismillah": None, "ayats": []}
        
        if item_type == "title":
            sura_groups[sura_name]["title"] = u
            sura_order.append(sura_name)
        elif item_type == "bismillah":
            sura_groups[sura_name]["bismillah"] = u
        elif item_type == "ayat":
            sura_groups[sura_name]["ayats"].append(u)
    
    # Handle suras that have ayats but no title on this page (continuation)
    for sura_name in sura_groups:
        if sura_name not in sura_order:
            # This is a continuation from previous page — put at beginning
            sura_order.insert(0, sura_name)
    
    # Step 2: Build the correct order
    correct_order = []
    
    # Prefix units first (istiaza, etc.)
    for u in prefix_units:
        correct_order.append(u)
    
    # Then each sura in order
    for sura_name in sura_order:
        group = sura_groups[sura_name]
        if group["title"]:
            correct_order.append(group["title"])
        if group["bismillah"]:
            correct_order.append(group["bismillah"])
        # Ayats sorted by their current sort_order (preserves internal order)
        for ayat in sorted(group["ayats"], key=lambda u: u["sort_order"]):
            correct_order.append(ayat)
    
    # Step 3: Check if reorder is needed
    old_order = [u["id"] for u in units]
    new_order = [u["id"] for u in correct_order]
    
    if old_order == new_order:
        return []  # Already correct
    
    # Step 4: Generate update actions
    updates = []
    for i, u in enumerate(correct_order):
        if u["sort_order"] != i:
            updates.append((u["id"], i))
    
    return updates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    print("Getting admin token...")
    token = get_token()
    print("Token obtained\n")
    
    r = requests.get(f"{API}/book/pages?limit=100")
    r.raise_for_status()
    all_pages = r.json()
    
    target_pages = sorted(
        [p for p in all_pages if 36 <= p["page_number"] <= 47],
        key=lambda p: p["page_number"]
    )
    
    total_fixed = 0
    
    for page_info in target_pages:
        page_id = page_info["id"]
        page_num = page_info["page_number"]
        
        data = get_page_data(page_num)
        units = sorted(data.get("text_units", []), key=lambda u: u["sort_order"])
        
        updates = reorder_page(units)
        
        if not updates:
            print(f"Page {page_num}: Already correct")
            continue
        
        total_fixed += 1
        print(f"Page {page_num}: {len(updates)} units to reorder")
        
        if args.dry_run:
            for uid, new_sort in updates:
                unit = next(u for u in units if u["id"] == uid)
                sec = (unit.get("metadata") or {}).get("section", "")
                old_sort = unit["sort_order"]
                text = unit["text_content"][:40]
                print(f"  {sec}: sort {old_sort} -> {new_sort}  ({text})")
        else:
            # Build bulk update actions
            actions = []
            for uid, new_sort in updates:
                actions.append({
                    "action": "update",
                    "id": uid,
                    "sort_order": new_sort,
                })
            
            try:
                result = bulk_update(token, page_id, actions)
                print(f"  Applied: {result.get('message', 'OK')}")
            except Exception as e:
                print(f"  Error: {e}")
        
        print()
    
    print(f"\n{'='*50}")
    if total_fixed == 0:
        print("All pages already correct!")
    else:
        print(f"{total_fixed} pages {'would be' if args.dry_run else ''} fixed.")
        if args.dry_run:
            print("Run without --dry-run to apply.")


if __name__ == "__main__":
    main()
