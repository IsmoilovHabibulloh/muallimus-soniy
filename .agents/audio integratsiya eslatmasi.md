# Audio Integratsiya Eslatmasi

## Arxitektura (3 bosqich)

```
AudioFile → AudioSegment → UnitSegmentMapping → TextUnit
```

1. **AudioFile** — yuklangan asl audio fayl (`01. muqova.mp3`)
2. **AudioSegment** — silence detection orqali ajratilgan segmentlar (content + silence)
3. **UnitSegmentMapping** — segment ↔ unit bog'lanishi (1:1, `is_published=true`)

---

## Sahifa audio mapping jarayoni

```
1. Audio faylni segmentlarga ajratish (auto_segment — FFmpeg silence detect)
2. Content segmentlarni kesish (sync-cut endpoint → individual .mp3 fayllar)
3. Segmentlarni unitlarga 1:1 tartib bilan moslashtirish (POST /mappings)
4. is_published = true qilish (SQL yoki admin panel)
5. Frontend deploy qilish
```

### API endpointlari
- `POST /api/v1/admin/audio/files/{id}/sync-cut` — segmentlarni kesish
- `POST /api/v1/admin/audio/mappings` — mapping yaratish (`text_unit_id`, `audio_segment_id`)
- `DELETE /api/v1/admin/audio/mappings/{id}` — mapping o'chirish
- `GET /api/v1/book/pages/{n}` — sahifa + `audio_segment_url` qaytaradi

### DB jadvallar
- `audio_files` — fayl ma'lumotlari
- `audio_segments` — segment (start_ms, end_ms, file_path, is_silence)
- `unit_segment_mappings` — bog'lanish (text_unit_id, audio_segment_id, is_published)

---

## Frontend audio player

> **MUHIM**: `just_audio` Flutter Web'da `setUrl()` ishlamaydi — bir marta set qilingan URL'ni almashtirib bo'lmaydi.

### Yechim: `WebAudioPlayer` (`lib/core/web_audio_player.dart`)
- `dart:js` orqali to'g'ridan-to'g'ri JavaScript `new Audio(url)` ishlatiladi
- Har safar `playUrl()` chaqirilganda eski audio to'xtatiladi va **yangi `Audio` element** yaratiladi
- `window.__muallimi_audio` global o'zgaruvchida saqlanadi
- `onended` callback orqali Dart tomonga signal yuboriladi

### Playback rejimlar
- **Unit-by-unit**: Agar unitlarda `audioSegmentUrl` bo'lsa, ketma-ket play (ustun)
- **Page audio**: Agar unitlarda segment bo'lmasa, sahifa audio faylini play (fallback)
- **Tap**: Har bir unitni alohida bosib eshitish mumkin

---

## Deploy — JUDA MUHIM!

> **Nginx to'g'ri yo'l**: `/root/muallimi-soniy/frontend/build/web/`  
> ❌ **NOTO'G'RI**: `/var/www/ikkinchimuallim/` (bu eski/boshqa papka!)

### To'g'ri deploy buyrug'i:
```bash
# Flutter build
cd frontend && flutter build web --release

# Serverga yuklash (TO'G'RI YO'L!)
sshpass -p 'codingtech2204' rsync -avz --delete \
  frontend/build/web/ \
  root@46.224.135.238:/root/muallimi-soniy/frontend/build/web/ \
  --exclude='media'
```

### Docker volume mapping:
```
/root/muallimi-soniy/frontend/build/web → /usr/share/nginx/web (nginx container)
/root/muallimi-soniy/admin/dist → /usr/share/nginx/admin
/var/lib/docker/volumes/muallimi-soniy_media_data/_data → /usr/share/nginx/media
```

---

## Xatolar va darslar

| Muammo | Sabab | Yechim |
|--------|-------|--------|
| `setUrl()` ishlamaydi | `just_audio` web bug | `dart:js` + `new Audio()` |
| Deploy ishlamaydi | Noto'g'ri papkaga rsync | `/root/muallimi-soniy/frontend/build/web/` |
| `debugPrint` ko'rinmaydi | Flutter release mode | `console.log` via JS eval |
| Nginx eski fayl beradi | Proxy cache | `nginx -s reload` yoki container restart |
| `audio_segment_url: null` | `is_published = false` | SQL UPDATE yoki admin panel |
