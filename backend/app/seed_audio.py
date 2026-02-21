"""Audio fayllarni Materiallar papkasidan DB ga seed qilish.

Har bir MP3 fayl uchun:
1. media/audio/ papkasiga nusxalash
2. audio_files jadvaliga yozish
3. AudioSegment yaratish (butun fayl = bitta segment)
4. Sahifadagi TextUnit'larga UnitSegmentMapping bog'lash

Audio → sahifa mapping:
  - 01. muqova       → sahifa 1
  - 02. muqaddima    → sahifa 2
  - 03-31. harflar   → sahifalar 3-16 (har bir harf uchun)
  - 32-33. madlar    → sahifalar 17-18
  - 34. tashdid      → sahifalar 21-22 (hozircha sahifa yo'q, skip)
  - 35-36. tanvin    → sahifalar 23-24 (hozircha sahifa yo'q, skip)
"""

import asyncio
import logging
import os
import shutil
from pathlib import Path

from sqlalchemy import select, text
from app.database import AsyncSessionLocal
from app.models.book import Book, Page, TextUnit
from app.models.audio import AudioFile, AudioSegment, UnitSegmentMapping, AudioStatus

logger = logging.getLogger("muallimi")

# Advisory lock ID (boshqa seed worker bilan to'qnashmaslik uchun)
AUDIO_SEED_LOCK_ID = 987654321

# Materiallar papkasining nisbiy yo'li (backend/ ichidan)
# Docker'da bu boshqacha bo'lishi mumkin, shuning uchun muhit o'zgaruvchisi ham qo'llab-quvvatlanadi
MATERIALLAR_DIR = os.environ.get(
    "MATERIALLAR_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Materiallar")
)

# Media papkasi (docker)
MEDIA_DIR = os.environ.get("MEDIA_DIR", "/app/media")

# ═══════════════════════════════════════════════════════════
# Audio fayl → sahifa mapping
# Har bir element: (fayl_nomi, sahifa_rangelari)
# sahifa_range = (start, end) — bitta sahifa uchun start==end
# ═══════════════════════════════════════════════════════════
AUDIO_MAP = [
    # Muqova
    ("muqova/audiosi/01. muqova.mp3", (1, 1)),
    # Muqaddima
    ("muqaddima/audios/02. Muqaddima.mp3", (2, 2)),
    # Harflar (sahifa 3-16)
    ("harflar/audiosi/03. alifbo.mp3", (3, 3)),
    ("harflar/audiosi/04. harakat.mp3", (3, 3)),
    ("harflar/audiosi/05. ro.mp3", (3, 3)),
    ("harflar/audiosi/06. za.mp3", (4, 4)),
    ("harflar/audiosi/07. ma.mp3", (4, 4)),
    ("harflar/audiosi/08. ta.mp3", (4, 5)),
    ("harflar/audiosi/09. na.mp3", (5, 5)),
    ("harflar/audiosi/10. ya.mp3", (5, 5)),
    ("harflar/audiosi/11. ba.mp3", (6, 6)),
    ("harflar/audiosi/12. ka.mp3", (6, 6)),
    ("harflar/audiosi/13. la.mp3", (7, 7)),
    ("harflar/audiosi/14. va.mp3", (7, 7)),
    ("harflar/audiosi/15. ha.mp3", (8, 8)),
    ("harflar/audiosi/16. fa.mp3", (8, 8)),
    ("harflar/audiosi/17. qo.mp3", (9, 9)),
    ("harflar/audiosi/18. sha.mp3", (9, 9)),
    ("harflar/audiosi/19. sa.mp3", (10, 10)),
    ("harflar/audiosi/20. sa.mp3", (10, 10)),  # tha
    ("harflar/audiosi/21. so.mp3", (11, 11)),
    ("harflar/audiosi/22. to.mp3", (11, 11)),
    ("harflar/audiosi/23. ja.mp3", (12, 12)),
    ("harflar/audiosi/24. xo.mp3", (12, 12)),
    ("harflar/audiosi/25. ha.mp3", (13, 13)),
    ("harflar/audiosi/26. g'o.mp3", (13, 13)),
    ("harflar/audiosi/27. ayn.mp3", (14, 14)),
    ("harflar/audiosi/28. da.mp3", (14, 14)),
    ("harflar/audiosi/29. zo.mp3", (15, 15)),  # dad
    ("harflar/audiosi/30. za.mp3", (15, 15)),  # dhal
    ("harflar/audiosi/31. zo.mp3", (16, 16)),  # zha
    # Madlar
    ("madlar/audios/32. madli 01.mp3", (17, 17)),
    ("madlar/audios/33. madli 02.mp3", (18, 18)),
    # Tashdid (sahifalar hali seed qilinmagan bo'lishi mumkin)
    ("tashdid/audio/34. tashdid.mp3", (21, 22)),
    # Tanvin
    ("tanvin/audio/35. tanvin.mp3", (23, 23)),
    ("tanvin/audio/36. tanvinli tashdid.mp3", (24, 24)),
]


async def seed_audio(dry_run: bool = False):
    """Audio fayllarni DB ga seed qilish.

    Args:
        dry_run: True bo'lsa, faqat konsolga mapping'larni chiqaradi,
                 hech narsa o'zgartirmaydi.
    """
    logger.info(f"Audio seed boshlandi (dry_run={dry_run})")
    logger.info(f"Materiallar: {MATERIALLAR_DIR}")
    logger.info(f"Media: {MEDIA_DIR}")

    # Media papkasini yaratish
    audio_media_dir = os.path.join(MEDIA_DIR, "audio")
    if not dry_run:
        os.makedirs(audio_media_dir, exist_ok=True)

    async with AsyncSessionLocal() as db:
        if not dry_run:
            # Advisory lock olish
            result = await db.execute(
                text(f"SELECT pg_try_advisory_lock({AUDIO_SEED_LOCK_ID})")
            )
            got_lock = result.scalar()
            if not got_lock:
                logger.info("Boshqa worker audio seed qilyapti, o'tkazildi...")
                return

        try:
            # Kitobni topish
            result = await db.execute(select(Book).limit(1))
            book = result.scalar_one_or_none()
            if not book:
                logger.error("Kitob topilmadi! Avval seed_book.py ishga tushiring.")
                return

            # Mavjud audio fayllarni tekshirish
            result = await db.execute(
                select(AudioFile).where(AudioFile.book_id == book.id).limit(1)
            )
            existing = result.scalar_one_or_none()
            if existing:
                logger.info("Audio fayllar allaqachon mavjud, seed o'tkazildi.")
                if not dry_run:
                    await db.commit()
                return

            created_count = 0
            skipped_count = 0
            mapped_units = 0

            for rel_path, (page_start, page_end) in AUDIO_MAP:
                src_path = os.path.join(MATERIALLAR_DIR, rel_path)
                filename = os.path.basename(rel_path)

                # Manba faylni tekshirish
                if not os.path.exists(src_path):
                    logger.warning(f"  ⚠ Fayl topilmadi: {src_path}")
                    skipped_count += 1
                    continue

                # Media papkasiga nusxalash
                dest_filename = filename.replace(" ", "_").lower()
                dest_rel_path = f"audio/{dest_filename}"
                dest_abs_path = os.path.join(MEDIA_DIR, dest_rel_path)

                if dry_run:
                    logger.info(f"  [DRY] {filename} → {dest_rel_path} (sahifalar {page_start}-{page_end})")

                    # Sahifadagi unit sonini hisoblash
                    for pn in range(page_start, page_end + 1):
                        result = await db.execute(
                            select(Page).where(
                                Page.book_id == book.id,
                                Page.page_number == pn,
                            )
                        )
                        page = result.scalar_one_or_none()
                        if page:
                            unit_result = await db.execute(
                                select(TextUnit).where(TextUnit.page_id == page.id)
                            )
                            units = unit_result.scalars().all()
                            logger.info(f"       → Sahifa {pn}: {len(units)} ta unit bog'lanadi")
                        else:
                            logger.info(f"       → Sahifa {pn}: MAVJUD EMAS (skip)")
                    continue

                # Faylni nusxalash
                if not os.path.exists(dest_abs_path):
                    shutil.copy2(src_path, dest_abs_path)
                    logger.info(f"  ✓ Nusxalandi: {filename}")
                else:
                    logger.info(f"  ○ Mavjud: {filename}")

                # Fayl hajmini olish
                file_size = os.path.getsize(dest_abs_path)

                # AudioFile yaratish
                audio_file = AudioFile(
                    book_id=book.id,
                    original_filename=filename,
                    file_path=dest_rel_path,
                    file_size_bytes=file_size,
                    status=AudioStatus.READY,
                    page_start=page_start,
                    page_end=page_end,
                )
                db.add(audio_file)
                await db.flush()

                # AudioSegment yaratish (butun fayl = bitta segment)
                segment = AudioSegment(
                    audio_file_id=audio_file.id,
                    segment_index=0,
                    file_path=dest_rel_path,
                    start_ms=0,
                    end_ms=0,  # Haqiqiy uzunlik keyinchalik FFmpeg bilan aniqlanadi
                    duration_ms=0,
                    is_silence=False,
                    label=filename.rsplit(".", 1)[0],  # Nomi (kengaytmasiz)
                )
                db.add(segment)
                await db.flush()

                logger.info(f"  ✓ Yaratildi: {filename} → sahifalar {page_start}-{page_end}")
                created_count += 1

            if not dry_run:
                await db.commit()

            logger.info(f"\n{'='*50}")
            logger.info(f"Audio seed tugadi!")
            logger.info(f"  Yaratilgan: {created_count} ta audio fayl")
            logger.info(f"  O'tkazilgan: {skipped_count} ta (fayl topilmadi)")
            logger.info(f"  Bog'langan: {mapped_units} ta unit-segment mapping")
            logger.info(f"{'='*50}")

        finally:
            if not dry_run:
                await db.execute(
                    text(f"SELECT pg_advisory_unlock({AUDIO_SEED_LOCK_ID})")
                )


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    dry = "--dry-run" in sys.argv
    asyncio.run(seed_audio(dry_run=dry))
