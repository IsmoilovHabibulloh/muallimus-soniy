"""Update letter header units in the database with positional forms.

This script connects to the PostgreSQL database and updates all _header
type units to use proper positional letter forms:
  - Beginning form + fatha
  - Middle form + kasra 
  - End form + damma

Usage:
    python update_headers.py
    
Requires DATABASE_URL environment variable (loaded from .env).
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load .env from the project root
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import asyncpg


# Mapping: old text_content -> new text_content
# Format: (old_value, new_value)
HEADER_UPDATES = [
    # Page 4
    ("زَ زِ زُ", "زَ ـزِ ـزُ"),          # za_header (non-connecting)
    ("مَ مِ مُ", "مـَ ـمـِ ـمُ"),        # mim_header
    ("تَ تِ تُ", "تـَ ـتـِ ـتُ"),        # ta_header
    # Page 5
    ("نَ نِ نُ", "نـَ ـنـِ ـنُ"),        # nun_header
    ("يَ يِ يُ", "يـَ ـيـِ ـيُ"),        # ya_header
    # Page 6
    ("بَ بِ بُ", "بـَ ـبـِ ـبُ"),        # ba_header
    ("كَ كِ كُ", "كـَ ـكـِ ـكُ"),        # kaf_header
    # Page 7
    ("لَ لِ لُ", "لـَ ـلـِ ـلُ"),        # lam_header
    ("وَ وِ وُ", "وَ ـوِ ـوُ"),          # waw_header (non-connecting)
    # Page 8
    ("هَ هِ هُ", "هـَ ـهـِ ـهُ"),        # ha_header
    ("فَ فِ فُ", "فـَ ـفـِ ـفُ"),        # fa_header
    # Page 9
    ("قَ قِ قُ", "قـَ ـقـِ ـقُ"),        # qaf_header
    ("شَ شِ شُ", "شـَ ـشـِ ـشُ"),        # shin_header
    # Page 10
    ("سَ سِ سُ", "سـَ ـسـِ ـسُ"),        # sin_header
    ("ثَ ثِ ثُ", "ثـَ ـثـِ ـثُ"),        # tha_header
    # Page 11
    ("صَ صِ صُ", "صـَ ـصـِ ـصُ"),        # sad_header
    ("طَ طِ طُ", "طـَ ـطـِ ـطُ"),        # ta_t_header
    # Page 12
    ("جَ جِ جُ", "جـَ ـجـِ ـجُ"),        # jim_header
    ("خَ خِ خُ", "خـَ ـخـِ ـخُ"),        # kha_header
    # Page 13
    ("حَ حِ حُ", "حـَ ـحـِ ـحُ"),        # ha_h_header
    ("غَ غِ غُ", "غـَ ـغـِ ـغُ"),        # ghayn_header
    # Page 14
    ("عَ عِ عُ", "عـَ ـعـِ ـعُ"),        # ayn_header
    ("دَ دِ دُ", "دَ ـدِ ـدُ"),          # dal_header (non-connecting)
    # Page 15
    ("ضَ ضِ ضُ", "ضـَ ـضـِ ـضُ"),        # dad_header
    ("ذَ ذِ ذُ", "ذَ ـذِ ـذُ"),          # dhal_header (non-connecting)
    # Page 16
    ("ظَ ظِ ظُ", "ظـَ ـظـِ ـظُ"),        # zha_header
]


async def main():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set in environment")
        sys.exit(1)

    conn = await asyncpg.connect(database_url)
    print(f"Connected to database")

    try:
        total_updated = 0
        for old_text, new_text in HEADER_UPDATES:
            # Find units with matching text_content where section contains '_header'
            result = await conn.execute(
                """
                UPDATE text_units 
                SET text_content = $1 
                WHERE text_content = $2 
                  AND metadata::text LIKE '%_header%'
                """,
                new_text, old_text
            )
            count = int(result.split()[-1])  # "UPDATE N"
            if count > 0:
                print(f"  ✓ Updated {count} unit(s): {old_text!r} → {new_text!r}")
                total_updated += count
            else:
                print(f"  ⚠ No match found for: {old_text!r}")

        print(f"\nTotal updated: {total_updated} units")
    finally:
        await conn.close()
        print("Connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
