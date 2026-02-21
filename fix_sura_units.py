#!/usr/bin/env python3
"""
Fix sura ayat splitting — ms-bbu task.

Problem: Sura ayats on pages 36-47 are split by physical line, not by ayat.
  Example: one unit contains "﴿١﴾ ... ﴿٢﴾" — two ayats in one unit.

Fix: For each sura section (*_ayat), concatenate all unit texts,
     then split at ﴿N﴾ markers so each ayat = 1 unit.

Usage:
  python fix_sura_units.py --dry-run   # Preview
  python fix_sura_units.py             # Apply
"""

import argparse
import re
import requests

API = "https://ikkinchimuallim.codingtech.uz/api/v1"
ADMIN_USER = "admin"
ADMIN_PASS = "MuallimuS2026!Adm"

# Matches ﴿١﴾, ﴿٢٣﴾ etc. — Arabic-Indic numerals between brackets
AYAT_SPLIT = re.compile(r'(﴿[٠-٩]+﴾)')


def get_token():
    r = requests.post(f"{API}/admin/auth/login", json={
        "username": ADMIN_USER, "password": ADMIN_PASS,
    })
    r.raise_for_status()
    return r.json()["access_token"]


def get_page_units(page_number):
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


def publish_page(token, page_id):
    r = requests.post(
        f"{API}/admin/book/pages/{page_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    r.raise_for_status()
    return r.json()


def split_text_into_ayats(full_text):
    """
    Split concatenated text into individual ayats.
    Each ayat ends with ﴿N﴾.
    
    Returns list of (ayat_text, marker) tuples.
    """
    parts = AYAT_SPLIT.split(full_text)
    ayats = []
    
    # parts alternates: text, marker, text, marker, ...
    # First part is text before first marker (should be start of ayat 1)
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and AYAT_SPLIT.match(parts[i + 1]):
            # text + marker = one ayat
            text = parts[i].strip()
            marker = parts[i + 1]
            ayat = f"{text} {marker}".strip()
            if ayat and ayat != marker:
                ayats.append(ayat)
            elif ayat == marker:
                # Marker only — append to previous ayat or skip
                pass
            i += 2
        else:
            # Trailing text without marker (shouldn't happen for valid sura)
            text = parts[i].strip()
            if text:
                ayats.append(text)
            i += 1
    
    return ayats


def process_sura_section(units, section_name):
    """
    Process all units belonging to one sura section.
    Returns (old_unit_ids, new_ayat_texts).
    """
    # Concatenate all text
    full_text = " ".join(u["text_content"].strip() for u in units)
    
    # Split into individual ayats
    ayats = split_text_into_ayats(full_text)
    
    old_ids = [u["id"] for u in units]
    
    return old_ids, ayats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("🔐 Getting admin token...")
    token = get_token()
    print("✅ Token obtained\n")

    # Get page list
    r = requests.get(f"{API}/book/pages?limit=100")
    r.raise_for_status()
    all_pages = r.json()

    # Sura pages only (36-47)
    target_pages = sorted(
        [p for p in all_pages if 36 <= p["page_number"] <= 47],
        key=lambda p: p["page_number"]
    )
    print(f"🎯 {len(target_pages)} sura pages (36-47)\n")

    total_old = 0
    total_new = 0

    for page_info in target_pages:
        page_id = page_info["id"]
        page_num = page_info["page_number"]

        data = get_page_units(page_num)
        all_units = sorted(data.get("text_units", []), key=lambda u: u["sort_order"])

        # Group ayat units by section
        ayat_sections = {}
        non_ayat_units = []
        for u in all_units:
            meta = (u.get("metadata") or {}).get("section", "")
            if "_ayat" in meta:
                if meta not in ayat_sections:
                    ayat_sections[meta] = []
                ayat_sections[meta].append(u)
            else:
                non_ayat_units.append(u)

        if not ayat_sections:
            print(f"📄 Page {page_num}: No ayat sections found")
            continue

        actions = []
        page_old = 0
        page_new = 0
        descriptions = []

        # Base sort_order for new ayat units
        # Start after the last non-ayat unit
        max_non_ayat_sort = max((u["sort_order"] for u in non_ayat_units), default=-1)
        next_sort = max_non_ayat_sort + 1

        for section_name in sorted(ayat_sections.keys()):
            section_units = ayat_sections[section_name]
            old_ids, new_ayats = process_sura_section(section_units, section_name)

            # Check if already correct
            if len(old_ids) == len(new_ayats):
                # Check if content is the same
                old_texts = [u["text_content"].strip() for u in section_units]
                if old_texts == [a.strip() for a in new_ayats]:
                    # Already correct — skip
                    for u in section_units:
                        next_sort = max(next_sort, u["sort_order"] + 1)
                    continue

            page_old += len(old_ids)
            page_new += len(new_ayats)

            # Delete all old ayat units
            for uid in old_ids:
                actions.append({"action": "delete", "id": uid})

            # Create new ayat units
            for ayat_text in new_ayats:
                actions.append({
                    "action": "create",
                    "unit_type": "sentence",
                    "text_content": ayat_text,
                    "sort_order": next_sort,
                    "metadata": {"section": section_name},
                })
                next_sort += 1

            descriptions.append(
                f"  {section_name}: {len(old_ids)} units → {len(new_ayats)} ayats"
            )

        if not actions:
            print(f"📄 Page {page_num}: ✅ Already correct")
            continue

        total_old += page_old
        total_new += page_new

        print(f"📄 Page {page_num}: 🔧 {page_old} old → {page_new} new ayats")
        for desc in descriptions:
            print(desc)

        if not args.dry_run:
            try:
                result = bulk_update(token, page_id, actions)
                print(f"   ✅ {result.get('message', 'Applied')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue

        print()

    print(f"\n{'=' * 50}")
    print(f"📊 Total: {total_old} old units → {total_new} proper ayats")
    if args.dry_run:
        print("⚠️  DRY RUN — run without --dry-run to apply.")
    else:
        print("✅ All changes applied!")


if __name__ == "__main__":
    main()
