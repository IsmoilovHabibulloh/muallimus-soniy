---
description: Yangi task olishda tasdiqlash jarayoni (Confirmation Loop)
---

# 📋 Task Tasdiqlash Jarayoni

Har qanday yangi task (vazifa) berilganda, **bajarishdan oldin** quyidagi qadamlarni qat'iy bajar:

## Qadamlar

### 1. Foydalanuvchi task beradi
- Foydalanuvchi yangi task/vazifa/buyruq beradi

### 2. Tushunganingni izohla
- Taskni o'z so'zlaring bilan qayta tushuntir
- Quyidagilarni aniq ko'rsat:
  - **Nima qilinadi** — aniq qanday o'zgarishlar bo'ladi
  - **Qayerda qilinadi** — qaysi fayllar, papkalar yoki tizimlar ta'sirlanadi
  - **Natija** — yakuniy natija qanday bo'ladi
- Hech qanday kodni o'zgartirma, hech narsa bajarma — faqat tushuntir

### 3. Tasdiqlashni kut
- Foydalanuvchidan **tasdiqlash** yoki **qo'shimcha** kutiladi:
  - ✅ **Tasdiqlansa** → 5-qadamga o't
  - ➕ **Qo'shimcha bo'lsa** → 4-qadamga o't

### 4. Qo'shimchalarni qo'sh
- Foydalanuvchi bergan qo'shimcha/o'zgartirishlarni kiriting
- Yangilangan to'liq tushuntirishni qayta yozib **2-qadamga** qayting
- Foydalanuvchi to'liq tasdiqlagunga qadar bu loop davom etadi

### 5. Ishni boshlash
- Foydalanuvchi to'liq tasdiqlagan so'ng, ishni boshlaysan
- Rejani bajar, kerak bo'lsa fayllarni o'zgartir, test qil

## ⚠️ Muhim Qoidalar

1. **Hech qachon** tasdiqlashsiz kod yozma yoki o'zgartirma
2. **Hech qachon** tasdiqlashsiz ma'lumotlar bazasiga yozma
3. Har bir yangi task uchun bu jarayon **qaytadan** boshlanadi
4. Agar task juda oddiy bo'lsa ham (masalan bitta qator o'zgartirish), baribir tasdiqlash kerak
5. Tasdiqlash so'ralganda faqat `notify_user` tool ishlatiladi

## 📝 Tasdiqlash Formati

Foydalanuvchiga yuboriladigan xabar quyidagi formatda bo'lsin:

```
## 🎯 Taskni tushundim

**Vazifa:** [task tavsifi]

**Qilinadigan ishlar:**
1. [ish 1]
2. [ish 2]
...

**Ta'sir qilinadigan fayllar:**
- `fayl_nomi.dart`
- `boshqa_fayl.py`

**Natija:** [kutilayotgan natija]

---
✅ Tasdiqlaysizmi yoki qo'shimcha bormi?
```
