---
description: Serverga deploy qilish (ikkinchimuallim.codingtech.uz)
---

# Server ma'lumotlari

| Parametr | Qiymat |
|----------|--------|
| IPv4 | `46.224.135.238` |
| IPv6 | `2a01:4f8:c014:4005::/64` |
| User | `root` |
| Password | `codingtech2204` |
| Domen | `ikkinchimuallim.codingtech.uz` |
| Server yo'li | `/root/muallimi-soniy` |
| Web yo'li | `/var/www/ikkinchimuallim` |

## Admin panel

| Parametr | Qiymat |
|----------|--------|
| URL | `https://ikkinchimuallim.codingtech.uz/admin/` |
| Login | `admin` |
| Parol | `MuallimuS2026!Adm` |

# Deploy jarayoni

## 1. Kodni git push qilish
// turbo
```bash
cd "/Users/habibulloh/Desktop/antigravity/Muallimus soniy"
git add -A && git commit -m "deploy: <qisqa tavsif>" && git push
```

## 2. Serverga SSH ulanish
```bash
sshpass -p 'codingtech2204' ssh -o StrictHostKeyChecking=no root@46.224.135.238
```

## 3. Kodni tortish va qayta build qilish
// turbo-all
```bash
sshpass -p 'codingtech2204' ssh -o StrictHostKeyChecking=no root@46.224.135.238 "cd /var/www/ikkinchimuallim && git pull && docker compose up --build -d"
```

## 4. Loglarni tekshirish
// turbo
```bash
sshpass -p 'codingtech2204' ssh -o StrictHostKeyChecking=no root@46.224.135.238 "cd /var/www/ikkinchimuallim && docker compose logs --tail 30 api"
```

## 5. Health check
// turbo
```bash
curl -sf https://ikkinchimuallim.codingtech.uz/api/v1/book/pages/1 | head -c 200
```

# Muhim eslatmalar

- Backend kodi `./backend/app:/app/app:ro` sifatida mount qilingan — restart yetarli
- Frontend uchun avval `flutter build web` kerak, keyin `frontend/build/web/` serverdagi nginx mount'iga joylash
- Media fayllar `media_data` Docker volume'da saqlanadi
- SSL sertifikatlari `/etc/letsencrypt/` da, certbot auto-renew cron orqali
