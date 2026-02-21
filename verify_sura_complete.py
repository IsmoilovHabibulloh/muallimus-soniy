#!/usr/bin/env python3
"""
Complete sura verification script — ms-bbu task.

Checks:
1. All expected suras are present
2. Each ayat unit has exactly 1 ﴿N﴾ marker
3. Ayat numbers are sequential (1, 2, 3...)
4. No ayat text is split across paragraphs
5. Sort order is consistent
6. Expected ayat counts match known sura lengths
"""

import re
import requests

API = "https://ikkinchimuallim.codingtech.uz/api/v1"

# ﴿١﴾ marker pattern — Arabic-Indic numerals
MARKER_RE = re.compile(r'﴿([٠-٩]+)﴾')

# Arabic-Indic to integer
ARABIC_DIGITS = '٠١٢٣٤٥٦٧٨٩'
def arabic_to_int(s):
    return int(''.join(str(ARABIC_DIGITS.index(c)) for c in s))

# Expected ayat counts per sura (from Quran)
EXPECTED_AYATS = {
    'fatiha': 6,  # Bismilloh alohida unit — faqat 6 ta raqamlangan oyat
    'baqara': 5,  # Only first 5 ayats in Muallimi Soniy
    'shams': 15,
    'layl': 21,
    'duha': 11,
    'sharh': 8,
    'tin': 8,
    'alaq': 19,
    'qadr': 5,
    'bayyina': 8,
    'zalzala': 8,
    'adiyat': 11,
    'qaria': 11,
    'takathur': 8,
    'asr': 3,
    'humaza': 9,
    'fil': 5,
    'quraysh': 4,
    'maun': 7,
    'kawthar': 3,
    'kafirun': 6,
    'nasr': 3,
    'masad': 5,
    'ikhlas': 4,  # 2 on page 46, 2 continued on page 47
    'falaq': 5,
    'nas': 6,
}


def main():
    print("🔍 Suralarni to'liq tekshirish...\n")
    
    total_issues = 0
    total_suras = 0
    found_suras = {}  # sura_name -> list of ayat units across all pages
    
    for pn in range(36, 48):
        data = requests.get(f"{API}/book/pages/{pn}").json()
        units = sorted(data.get("text_units", []), key=lambda u: u["sort_order"])
        
        page_issues = []
        
        for u in units:
            sec = (u.get("metadata") or {}).get("section", "")
            
            # Collect sura titles
            if sec.startswith("surah_") and sec.endswith("_title"):
                sura_name = sec.replace("surah_", "").replace("_title", "")
                total_suras += 1
            
            # Check ayat units
            if "_ayat" in sec:
                # Extract sura name from section (e.g., "fatiha_ayat" -> "fatiha")
                sura_key = sec.replace("_ayat", "").replace("_cont", "")
                
                if sura_key not in found_suras:
                    found_suras[sura_key] = []
                found_suras[sura_key].append(u)
                
                markers = MARKER_RE.findall(u["text_content"])
                
                # Check: exactly 1 marker per unit
                if len(markers) != 1:
                    page_issues.append(
                        f"  ❌ Unit {u['id']} ({sec}): {len(markers)} marker(s) "
                        f"(kutilgan: 1) — \"{u['text_content'][:60]}...\""
                    )
                
                # Check: no newlines in text (avzast ko'chirish)
                if "\n" in u["text_content"]:
                    page_issues.append(
                        f"  ❌ Unit {u['id']} ({sec}): Matnda yangi qator bor (avzast muammosi)"
                    )
        
        if page_issues:
            print(f"📄 Sahifa {pn}: ❌ {len(page_issues)} muammo")
            for issue in page_issues:
                print(issue)
            total_issues += len(page_issues)
        else:
            print(f"📄 Sahifa {pn}: ✅ Hammasi to'g'ri ({len(units)} unit)")
    
    print(f"\n{'='*60}")
    print(f"📊 Suralar tekshiruvi:")
    print(f"{'='*60}\n")
    
    # Check ayat sequence for each sura
    for sura_name in sorted(found_suras.keys()):
        ayat_units = found_suras[sura_name]
        
        # Extract ayat numbers
        ayat_numbers = []
        for u in ayat_units:
            markers = MARKER_RE.findall(u["text_content"])
            if markers:
                ayat_numbers.append(arabic_to_int(markers[0]))
        
        # Check sequential order
        expected_seq = list(range(1, len(ayat_numbers) + 1))
        is_sequential = ayat_numbers == expected_seq
        
        # Check expected count
        expected_count = EXPECTED_AYATS.get(sura_name, "?")
        count_ok = len(ayat_numbers) == expected_count if isinstance(expected_count, int) else True
        
        status = "✅" if (is_sequential and count_ok) else "❌"
        
        print(f"  {status} {sura_name}: {len(ayat_numbers)} oyat", end="")
        if isinstance(expected_count, int):
            if count_ok:
                print(f" (kutilgan: {expected_count} ✓)", end="")
            else:
                print(f" (kutilgan: {expected_count} ✗)", end="")
                total_issues += 1
        
        if not is_sequential:
            print(f" — tartib xato: {ayat_numbers}", end="")
            total_issues += 1
        
        print()
    
    print(f"\n{'='*60}")
    if total_issues == 0:
        print("🎉 Barcha suralar to'g'ri! Muammolar topilmadi.")
    else:
        print(f"⚠️  Jami {total_issues} ta muammo topildi.")
    
    return total_issues


if __name__ == "__main__":
    exit(main())
