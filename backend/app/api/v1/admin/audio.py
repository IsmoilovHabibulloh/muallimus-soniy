"""Admin audio management endpoints."""

import os
import shutil
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.deps import get_current_admin
from app.models.admin import AdminUser
from app.models.audio import AudioFile, AudioSegment, UnitSegmentMapping, AudioStatus
from app.models.book import TextUnit
from app.models.system import AuditLog
from app.schemas.audio import AudioFileOut, AudioSegmentOut, AudioSegmentUpdate, SegmentMappingCreate, SegmentMappingOut
from app.config import get_settings
from app.utils.validators import validate_file_extension, sanitize_filename

logger = logging.getLogger("muallimi")

router = APIRouter(prefix="/audio", tags=["Admin Audio"])
settings = get_settings()


# ═══════════════════════════════════════════════════════════
# Upload & list
# ═══════════════════════════════════════════════════════════

@router.post("/upload", response_model=AudioFileOut, status_code=201)
async def upload_audio(
    file: UploadFile = File(...),
    book_id: int = Form(...),
    page_start: int = Form(None),
    page_end: int = Form(None),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upload an MP3 audio file for processing."""
    if not file.filename or not validate_file_extension(file.filename, ["mp3"]):
        raise HTTPException(status_code=400, detail="Faqat MP3 fayl qabul qilinadi")

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Fayl hajmi {settings.MAX_UPLOAD_SIZE_MB}MB dan oshmasligi kerak"
        )

    safe_name = sanitize_filename(file.filename)
    upload_dir = os.path.join(settings.MEDIA_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join("uploads", safe_name)
    full_path = os.path.join(settings.MEDIA_DIR, file_path)

    with open(full_path, "wb") as f:
        f.write(content)

    audio_file = AudioFile(
        book_id=book_id,
        original_filename=file.filename,
        file_path=file_path,
        file_size_bytes=len(content),
        status=AudioStatus.UPLOADED,
        page_start=page_start,
        page_end=page_end,
    )
    db.add(audio_file)
    await db.flush()

    db.add(AuditLog(
        admin_id=admin.id,
        action="upload_audio",
        entity_type="audio_file",
        entity_id=audio_file.id,
        details={"filename": file.filename},
    ))

    return AudioFileOut(
        id=audio_file.id,
        book_id=audio_file.book_id,
        original_filename=audio_file.original_filename,
        file_size_bytes=audio_file.file_size_bytes,
        status=audio_file.status.value,
        page_start=page_start,
        page_end=page_end,
        created_at=audio_file.created_at,
    )


@router.get("/files", response_model=List[AudioFileOut])
async def list_audio_files(
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AudioFile)
        .options(selectinload(AudioFile.segments))
        .order_by(AudioFile.created_at.desc())
    )
    files = result.scalars().all()
    out = []
    for af in files:
        seg_count = len(af.segments) if af.segments else 0
        out.append(AudioFileOut(
            id=af.id,
            book_id=af.book_id,
            original_filename=af.original_filename,
            duration_ms=af.duration_ms,
            file_size_bytes=af.file_size_bytes,
            status=af.status.value if hasattr(af.status, 'value') else af.status,
            error_message=af.error_message,
            page_start=af.page_start,
            page_end=af.page_end,
            waveform_peaks=af.waveform_peaks,
            segment_count=seg_count,
            created_at=af.created_at,
        ))
    return out


# ═══════════════════════════════════════════════════════════
# Segments CRUD
# ═══════════════════════════════════════════════════════════

@router.get("/files/{audio_file_id}/segments", response_model=List[AudioSegmentOut])
async def get_segments(
    audio_file_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AudioSegment)
        .where(AudioSegment.audio_file_id == audio_file_id)
        .order_by(AudioSegment.segment_index)
    )
    segments = result.scalars().all()
    return [
        AudioSegmentOut(
            id=s.id,
            segment_index=s.segment_index,
            file_url=f"{settings.MEDIA_BASE_URL}/{s.file_path}" if s.file_path else None,
            start_ms=s.start_ms,
            end_ms=s.end_ms,
            duration_ms=s.duration_ms,
            waveform_peaks=s.waveform_peaks,
            is_silence=s.is_silence,
            label=s.label,
            version=s.version,
        )
        for s in segments
    ]


@router.put("/segments/{segment_id}", response_model=AudioSegmentOut)
async def update_segment(
    segment_id: int,
    data: AudioSegmentUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update segment boundaries."""
    result = await db.execute(select(AudioSegment).where(AudioSegment.id == segment_id))
    seg = result.scalar_one_or_none()
    if not seg:
        raise HTTPException(status_code=404, detail="Segment topilmadi")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(seg, field, value)

    if data.start_ms is not None or data.end_ms is not None:
        seg.duration_ms = seg.end_ms - seg.start_ms

    await db.flush()
    db.add(AuditLog(admin_id=admin.id, action="update", entity_type="audio_segment", entity_id=segment_id))

    return AudioSegmentOut(
        id=seg.id,
        segment_index=seg.segment_index,
        file_url=f"{settings.MEDIA_BASE_URL}/{seg.file_path}" if seg.file_path else None,
        start_ms=seg.start_ms,
        end_ms=seg.end_ms,
        duration_ms=seg.duration_ms,
        waveform_peaks=seg.waveform_peaks,
        is_silence=seg.is_silence,
        label=seg.label,
        version=seg.version,
    )


@router.delete("/segments/{segment_id}")
async def delete_segment(
    segment_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a single segment."""
    result = await db.execute(select(AudioSegment).where(AudioSegment.id == segment_id))
    seg = result.scalar_one_or_none()
    if not seg:
        raise HTTPException(status_code=404, detail="Segment topilmadi")

    # Delete segment file if exists
    if seg.file_path:
        fpath = os.path.join(settings.MEDIA_DIR, seg.file_path)
        if os.path.exists(fpath):
            os.remove(fpath)

    await db.delete(seg)
    db.add(AuditLog(admin_id=admin.id, action="delete", entity_type="audio_segment", entity_id=segment_id))
    return {"message": "Segment o'chirildi"}


# ═══════════════════════════════════════════════════════════
# Segment ↔ Unit Mapping
# ═══════════════════════════════════════════════════════════

@router.post("/mappings", response_model=SegmentMappingOut, status_code=201)
async def create_mapping(
    data: SegmentMappingCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Map an audio segment to a text unit."""
    unit = await db.get(TextUnit, data.text_unit_id)
    segment = await db.get(AudioSegment, data.audio_segment_id)
    if not unit or not segment:
        raise HTTPException(status_code=404, detail="Birlik yoki segment topilmadi")

    mapping = UnitSegmentMapping(
        text_unit_id=data.text_unit_id,
        audio_segment_id=data.audio_segment_id,
    )
    db.add(mapping)
    await db.flush()
    db.add(AuditLog(admin_id=admin.id, action="create", entity_type="mapping", entity_id=mapping.id))
    return mapping


@router.delete("/mappings/{mapping_id}")
async def delete_mapping(
    mapping_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UnitSegmentMapping).where(UnitSegmentMapping.id == mapping_id))
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping topilmadi")
    await db.delete(mapping)
    db.add(AuditLog(admin_id=admin.id, action="delete", entity_type="mapping", entity_id=mapping_id))
    return {"message": "Mapping o'chirildi"}


# ═══════════════════════════════════════════════════════════
# SYNC Processing — Celery'siz to'g'ridan-to'g'ri ishlash
# ═══════════════════════════════════════════════════════════

@router.post("/files/{audio_file_id}/sync-process")
async def sync_process_audio(
    audio_file_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Sinxron audio processing: davomiylik, waveform, auto-segmentatsiya.
    Celery'ga bog'liq emas — to'g'ridan-to'g'ri FFmpeg chaqiradi.
    """
    import asyncio
    from app.services.audio_processor import (
        get_audio_duration_ms, generate_waveform_peaks, auto_segment,
    )

    audio_file = await db.get(AudioFile, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi")

    source_path = os.path.join(settings.MEDIA_DIR, audio_file.file_path)
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail=f"Audio fayl topilmadi: {audio_file.file_path}")

    audio_file.status = AudioStatus.PROCESSING
    await db.flush()

    try:
        # Run FFmpeg in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        # 1. Duration
        duration = await loop.run_in_executor(None, get_audio_duration_ms, source_path)
        audio_file.duration_ms = duration

        # 2. Waveform peaks
        peaks = await loop.run_in_executor(None, generate_waveform_peaks, source_path)
        audio_file.waveform_peaks = peaks

        # 3. Auto-segment
        segments_data = await loop.run_in_executor(
            None, auto_segment, source_path, duration
        )

        # Delete old segments
        await db.execute(
            sa_delete(AudioSegment).where(AudioSegment.audio_file_id == audio_file_id)
        )

        # Create new segments
        for seg_info in segments_data:
            segment = AudioSegment(
                audio_file_id=audio_file.id,
                segment_index=seg_info["segment_index"],
                start_ms=seg_info["start_ms"],
                end_ms=seg_info["end_ms"],
                duration_ms=seg_info["duration_ms"],
                is_silence=seg_info["is_silence"],
            )
            db.add(segment)

        audio_file.status = AudioStatus.SEGMENTED
        audio_file.error_message = None
        audio_file.processing_metadata = {
            "segment_count": len(segments_data),
            "duration_ms": duration,
            "peaks_count": len(peaks),
        }
        await db.commit()

        logger.info(f"Sync process complete: {len(segments_data)} segments, {duration}ms")

        return {
            "message": f"Audio qayta ishlandi: {len(segments_data)} ta segment topildi",
            "duration_ms": duration,
            "segment_count": len(segments_data),
            "status": "segmented",
        }

    except Exception as e:
        audio_file.status = AudioStatus.ERROR
        audio_file.error_message = str(e)[:500]
        await db.commit()
        logger.error(f"Sync process error: {e}")
        raise HTTPException(status_code=500, detail=f"Qayta ishlashda xatolik: {str(e)[:200]}")


@router.post("/files/{audio_file_id}/sync-cut")
async def sync_cut_segments(
    audio_file_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Sinxron segment kesish: har bir segmentni alohida MP3 faylga ajratish.
    Celery'ga bog'liq emas — to'g'ridan-to'g'ri FFmpeg chaqiradi.
    """
    import asyncio
    from app.services.audio_processor import cut_segment_file

    audio_file = await db.get(AudioFile, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi")

    source_path = os.path.join(settings.MEDIA_DIR, audio_file.file_path)
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi diskda")

    # Get non-silence segments
    result = await db.execute(
        select(AudioSegment)
        .where(
            AudioSegment.audio_file_id == audio_file_id,
            AudioSegment.is_silence == False,
        )
        .order_by(AudioSegment.segment_index)
    )
    segments = result.scalars().all()

    if not segments:
        raise HTTPException(status_code=400, detail="Kesilishi kerak segmentlar yo'q")

    segments_dir = os.path.join(settings.MEDIA_DIR, "segments")
    os.makedirs(segments_dir, exist_ok=True)

    loop = asyncio.get_event_loop()
    cut_count = 0
    errors = []

    for seg in segments:
        if seg.start_ms >= seg.end_ms:
            errors.append(f"Segment #{seg.segment_index}: noto'g'ri chegaralar ({seg.start_ms}-{seg.end_ms})")
            continue

        filename = f"seg_{audio_file_id}_{seg.segment_index:04d}_v{seg.version}.mp3"
        output_path = os.path.join(segments_dir, filename)

        success = await loop.run_in_executor(
            None, cut_segment_file, source_path, output_path, seg.start_ms, seg.end_ms
        )

        if success:
            seg.file_path = f"segments/{filename}"
            cut_count += 1
        else:
            errors.append(f"Segment #{seg.segment_index}: kesish amalga oshmadi")

    audio_file.status = AudioStatus.READY
    await db.commit()

    db.add(AuditLog(
        admin_id=admin.id,
        action="sync_cut_segments",
        entity_type="audio_file",
        entity_id=audio_file_id,
        details={"cut_count": cut_count, "errors": errors},
    ))

    msg = f"{cut_count} ta segment kesildi"
    if errors:
        msg += f" ({len(errors)} ta xatolik)"

    return {"message": msg, "cut_count": cut_count, "errors": errors, "status": "ready"}


# ═══════════════════════════════════════════════════════════
# Audio play & file management
# ═══════════════════════════════════════════════════════════

@router.get("/files/{audio_file_id}/play")
async def get_audio_play_url(
    audio_file_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Return the media URL for an audio file."""
    audio_file = await db.get(AudioFile, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi")

    return {
        "url": f"{settings.MEDIA_BASE_URL}/{audio_file.file_path}",
        "filename": audio_file.original_filename,
        "duration_ms": audio_file.duration_ms,
    }


@router.delete("/files/{audio_file_id}")
async def delete_audio_file(
    audio_file_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete an audio file and all its segments."""
    audio_file = await db.get(AudioFile, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi")

    # Delete physical files
    fpath = os.path.join(settings.MEDIA_DIR, audio_file.file_path)
    if os.path.exists(fpath):
        os.remove(fpath)

    # Delete segment files
    result = await db.execute(
        select(AudioSegment).where(AudioSegment.audio_file_id == audio_file_id)
    )
    for seg in result.scalars().all():
        if seg.file_path:
            sfpath = os.path.join(settings.MEDIA_DIR, seg.file_path)
            if os.path.exists(sfpath):
                os.remove(sfpath)

    await db.delete(audio_file)  # cascade deletes segments
    db.add(AuditLog(
        admin_id=admin.id,
        action="delete",
        entity_type="audio_file",
        entity_id=audio_file_id,
    ))

    return {"message": "Audio fayl o'chirildi"}


# ═══════════════════════════════════════════════════════════
# Legacy Celery endpoints (backward compat)
# ═══════════════════════════════════════════════════════════

@router.post("/files/{audio_file_id}/cut-segments")
async def cut_segments(
    audio_file_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Trigger FFmpeg to cut individual segment audio files (Celery)."""
    audio_file = await db.get(AudioFile, audio_file_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio fayl topilmadi")

    try:
        from app.tasks.audio_tasks import cut_segments_task
        task = cut_segments_task.delay(audio_file_id)
        task_id = task.id
    except Exception:
        task_id = "celery_unavailable"

    db.add(AuditLog(
        admin_id=admin.id,
        action="cut_segments",
        entity_type="audio_file",
        entity_id=audio_file_id,
        details={"task_id": task_id},
    ))

    return {"message": "Segmentlar kesish boshlandi", "task_id": task_id}
