import 'package:flutter/material.dart';
import '../../core/theme/colors.dart';

class LegalScreen extends StatelessWidget {
  final String title;
  final String type; // 'privacy', 'terms', 'about'

  const LegalScreen({
    super.key,
    required this.title,
    required this.type,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: _buildContent(context, isDark),
        ),
      ),
    );
  }

  List<Widget> _buildContent(BuildContext context, bool isDark) {
    switch (type) {
      case 'privacy':
        return _privacyContent(context, isDark);
      case 'terms':
        return _termsContent(context, isDark);
      case 'about':
        return _aboutContent(context, isDark);
      default:
        return [];
    }
  }

  // ===================== MAXFIYLIK SIYOSATI =====================
  List<Widget> _privacyContent(BuildContext context, bool isDark) {
    return [
      _header(context, '🔒 Maxfiylik siyosati', 'Kuchga kirgan: 2026-yil, 16-fevral', isDark),

      _sectionTitle(context, '1. Kirish'),
      _paragraph('Ushbu Maxfiylik siyosati "MYSTAR" MChJ tomonidan ishlab chiqilgan "Muallimi Soniy" mobil ilovasi foydalanuvchilarining shaxsiy ma\'lumotlarini to\'plash, saqlash, qayta ishlash va himoya qilish tartibini belgilaydi.'),
      _paragraph('Ilovadan foydalanishni boshlash orqali Siz ushbu Maxfiylik siyosati shartlariga rozilik bildirasiz.'),

      _sectionTitle(context, '2. Biz to\'playdigan ma\'lumotlar'),
      _subtitle(context, '2.1. Ixtiyoriy ma\'lumotlar'),
      _paragraph('Ilova faqat "Fikr bildirish" bo\'limi orqali quyidagi ma\'lumotlarni qabul qiladi:'),
      _dataTable(isDark),
      _highlightBox('⚠️ Muhim: Ushbu ma\'lumotlar faqat foydalanuvchi "Fikr bildirish" formasini ixtiyoriy ravishda to\'ldirib, "Yuborish" tugmasini bosgan taqdirdagina to\'planadi. Ilova avtomatik ravishda hech qanday shaxsiy ma\'lumotni to\'plamaydi.', isDark),

      _subtitle(context, '2.2. Mahalliy saqlash'),
      _paragraph('Ilova quyidagi texnik ma\'lumotlarni faqat qurilmada mahalliy saqlaydi va serverga yubormaydi:'),
      _bulletList([
        'Tanlangan til sozlamasi',
        'Tanlangan mavzu (kunduzgi/tungi rejim)',
        'Oxirgi o\'qilgan sahifa raqami',
      ]),

      _subtitle(context, '2.3. Biz to\'plaMAYDIGAN ma\'lumotlar'),
      _bulletList([
        'GPS joylashuv ma\'lumotlari',
        'Kontaktlar, suratlar yoki qurilmadagi fayllar',
        'Qurilma identifikatorlari (IMEI, MAC)',
        'Reklama identifikatorlari',
        'Moliyaviy yoki to\'lov ma\'lumotlari',
        'Biometrik va sog\'liq ma\'lumotlari',
      ]),

      _sectionTitle(context, '3. Ma\'lumotlardan foydalanish'),
      _paragraph('"Fikr bildirish" orqali olingan ma\'lumotlar faqat quyidagi maqsadlarda ishlatiladi:'),
      _bulletList([
        'Foydalanuvchi murojaatlariga javob berish',
        'Ilovadagi xatolarni tuzatish',
        'Ilova sifatini oshirish',
      ]),
      _paragraph('Ma\'lumotlar marketing, reklama yoki profillash maqsadlarida ishlatilmaydi.'),

      _sectionTitle(context, '4. Uchinchi shaxslarga berish'),
      _paragraph('Biz foydalanuvchilarning shaxsiy ma\'lumotlarini uchinchi shaxslarga sotmaymiz, ijaraga bermaymiz yoki tijorat maqsadlarida bermaymiz.'),
      _paragraph('Ma\'lumotlar faqat O\'zbekiston Respublikasi qonunchiligiga muvofiq vakolatli davlat organlarining yozma talabi yoki foydalanuvchining roziligi bilan berilishi mumkin.'),

      _sectionTitle(context, '5. Saqlash va himoya'),
      _bulletList([
        'Barcha ma\'lumotlar HTTPS (TLS/SSL) orqali shifrlangan',
        'Server ma\'lumotlari xavfsiz muhitda saqlanadi',
        'Ma\'lumotlarga faqat vakolatli xodimlar kira oladi',
        'Ma\'lumotlar 90 kun ichida o\'chiriladi',
      ]),

      _sectionTitle(context, '6. Foydalanuvchi huquqlari'),
      _bulletList([
        'Ma\'lumotlarni so\'rash huquqi',
        'Ma\'lumotlarni o\'chirish huquqi',
        'Ma\'lumotlarni tuzatish huquqi',
        'Rozilikni bekor qilish huquqi',
      ]),
      _paragraph('Murojaatlar uchun: shohruxbekaralov@gmail.com\nJavob muddati: 30 kun'),

      _sectionTitle(context, '7. Bolalar maxfiyligi'),
      _paragraph('Ilova ta\'limiy xarakterga ega. Biz 13 yoshdan kichik bolalardan ataylab shaxsiy ma\'lumot to\'plamaymiz.'),

      _sectionTitle(context, '8. Uchinchi tomon xizmatlari'),
      _paragraph('Ilova uchinchi tomon analitika, reklama yoki kuzatish xizmatlaridan foydalanmaydi.'),

      _sectionTitle(context, '9. Amaldagi qonunchilik'),
      _bulletList([
        'O\'zR "Shaxsga doir ma\'lumotlar to\'g\'risida"gi Qonuni (O\'RQ-547)',
        'O\'zR "Axborot erkinligi" Qonuni',
        'Google Play Developer Distribution Agreement',
        'Apple Developer Program License Agreement',
      ]),

      _sectionTitle(context, '10. Bog\'lanish'),
      _contactInfo(isDark),

      const SizedBox(height: 32),
      _footer('© 2026 MYSTAR MChJ. Barcha huquqlar himoyalangan.', isDark),
    ];
  }

  // ===================== FOYDALANISH SHARTLARI =====================
  List<Widget> _termsContent(BuildContext context, bool isDark) {
    return [
      _header(context, '📋 Foydalanish shartlari', 'Kuchga kirgan: 2026-yil, 16-fevral', isDark),

      _sectionTitle(context, '1. Umumiy qoidalar'),
      _paragraph('Ushbu Shartlar "MYSTAR" MChJ tomonidan ishlab chiqilgan "Muallimi Soniy" mobil ilovasidan foydalanish tartib va qoidalarini belgilaydi.'),
      _paragraph('Ilovani o\'rnatish yoki foydalanish orqali Siz ushbu Shartlarga rozilik bildirasiz.'),

      _sectionTitle(context, '2. Ilova tavsifi'),
      _paragraph('"Muallimi Soniy" — Ahmad Xodiy Maqsudiy tomonidan yozilgan kitobning raqamli versiyasi bo\'lib, arab alifbosini interaktiv o\'rganish uchun mo\'ljallangan bepul ta\'limiy ilovadir.'),
      _highlightBox('📖 Huquqiy asos: O\'zbekiston Respublikasi Vazirlar Mahkamasi huzuridagi Din ishlari bo\'yicha qo\'mitaning 2014-yil 10-noyabrdagi 3438-son xulosasi asosida nashr etilgan "Muallimi soniy" kitobi va MP3 diskidan foydalanilgan.', isDark),

      _sectionTitle(context, '3. Berilgan huquqlar'),
      _bulletList([
        'Ilovani bepul yuklab olish va o\'rnatish',
        'Barcha funksiyalardan cheklanmagan foydalanish',
        'Kontentni shaxsiy ta\'limiy maqsadlarda o\'qish va tinglash',
      ]),

      _sectionTitle(context, '4. Taqiqlangan harakatlar'),
      _bulletList([
        'Kontentni tijorat maqsadlarida foydalanish yoki sotish',
        'Ilovani dekompile yoki reverse-engineering qilish',
        'Ilova xavfsizlik tizimlarini chetlab o\'tish',
        'Ilovadan noqonuniy maqsadlarda foydalanish',
        'Ilova serverlariga zarar yetkazish',
      ]),

      _sectionTitle(context, '5. Dasturiy kod litsenziyasi'),
      _paragraph('Dasturiy kod Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) litsenziyasi ostida tarqatiladi.'),
      _bulletList([
        '✅ Kodni ko\'rish, o\'rganish va o\'zgartirish mumkin',
        '✅ Notijorat maqsadlarda tarqatish mumkin',
        '❌ Tijorat maqsadida foydalanish TAQIQLANADI',
        '❌ Sotish yoki pulli xizmat sifatida taqdim etish TAQIQLANADI',
      ]),

      _sectionTitle(context, '6. Javobgarlik cheklovi'),
      _paragraph('Ilova "MAVJUD HOLDA" (AS IS) taqdim etiladi. Kompaniya ilovaning uzluksiz yoki xatosiz ishlashini kafolatlamaydi.'),

      _sectionTitle(context, '7. Internet ulanishi'),
      _paragraph('Ilova asosan oflayn rejimda ishlaydi. Internet faqat quyidagi hollarda talab qilinadi:'),
      _bulletList([
        'Birinchi ishga tushirish va kontent yuklash',
        'Yangilanishlarni yuklab olish',
        '"Fikr bildirish" formasini yuborish',
      ]),

      _sectionTitle(context, '8. Intellektual mulk'),
      _paragraph('Asl kitob matni Ahmad Xodiy Maqsudiy qalamiga mansub. VazMahkama huzuridagi Din ishlari qo\'mitasining 2014-yil 10-noyabrdagi 3438-son xulosasi asosida nashr etilgan.'),
      _paragraph('Audio yozuvlar: Jahongir qori Nematov.'),

      _sectionTitle(context, '9. Nizolarni hal qilish'),
      _paragraph('Barcha nizolar avval muzokaralar yo\'li bilan, muzokaralar natija bermaganida O\'zbekiston Respublikasi qonunchiligiga muvofiq hal qilinadi.'),

      _sectionTitle(context, '10. Bog\'lanish'),
      _contactInfo(isDark),

      const SizedBox(height: 32),
      _footer('© 2026 MYSTAR MChJ. Barcha huquqlar himoyalangan.', isDark),
    ];
  }

  // ===================== DASTUR HAQIDA =====================
  List<Widget> _aboutContent(BuildContext context, bool isDark) {
    return [
      _header(context, '📖 Dastur haqida', 'Muallimi Soniy — Ikkinchi Muallim', isDark),

      _appInfoTable(isDark),

      _sectionTitle(context, '1. Ilova haqida'),
      _paragraph('"Muallimi Soniy" (المعلم الثاني — Ikkinchi Muallim) — mashhur islom olimi Ahmad Xodiy Maqsudiy tomonidan yozilgan arab alifbosini o\'rgatishga bag\'ishlangan klassik darslikning zamonaviy raqamli versiyasidir.'),
      _highlightBox('📜 Huquqiy asos: O\'zbekiston Respublikasi Vazirlar Mahkamasi huzuridagi Din ishlari bo\'yicha qo\'mitaning 2014-yil 10-noyabrdagi 3438-son xulosasi asosida nashr etilgan "Muallimi soniy" kitobi va MP3 diskidan foydalanilgan.', isDark),

      _sectionTitle(context, '2. Muallif haqida'),
      _paragraph('Ahmad Xodiy Maqsudiy (1868–1941) — tatar-boshqird pedagogi, yozuvchi va islom olimi. "Muallimi Soniy" uning eng mashhur asarlaridan bo\'lib, arab alifbosini bosqichma-bosqich o\'rgatish uchun mo\'ljallangan.'),

      _sectionTitle(context, '3. Audio'),
      _paragraph('Barcha sahifalarning ovozli talaffuzini Jahongir qori Nematov o\'qigan. 16 sahifa, MP3 formatda.'),

      _sectionTitle(context, '4. Imkoniyatlar'),
      _bulletList([
        '📚 16 sahifa raqamlashtirilgan kitob',
        '🔊 Professional ovozli talaffuz',
        '🌙 Kunduzgi va tungi rejim',
        '🌐 5 tilda interfeys',
        '📱 Oflayn rejim',
        '💬 Fikr bildirish',
        '🆓 Butunlay bepul',
      ]),

      _sectionTitle(context, '5. Texnologiyalar'),
      _techBadges(isDark),

      _sectionTitle(context, '6. Ochiq manba'),
      _paragraph('Dasturiy kod CC BY-NC 4.0 litsenziyasi ostida ochiq (open source).'),
      _paragraph('GitHub: github.com/IsmoilovHabibulloh/muallimus-soniy'),

      _sectionTitle(context, '7. Nashr ma\'lumotlari'),
      _publishInfoTable(isDark),

      _sectionTitle(context, '8. Tashakkur'),
      _bulletList([
        'O\'zbekiston Musulmonlar Idorasi',
        'Din ishlari bo\'yicha qo\'mita (3438-son xulosa)',
        'Jahongir qori Nematov — audio yozuvlar',
        'Ahmad Xodiy Maqsudiy rahmatullohi — asar muallifi',
        'Flutter va Open Source hamjamiyati',
      ]),

      _sectionTitle(context, '9. Bog\'lanish'),
      _contactInfo(isDark),

      const SizedBox(height: 32),
      _footer('© 2026 MYSTAR MChJ. Barcha huquqlar himoyalangan.\n© 2014 O\'zbekiston Musulmonlar Idorasi.', isDark),
    ];
  }

  // ===================== HELPER WIDGETS =====================

  Widget _header(BuildContext context, String title, String subtitle, bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppColors.primary,
            AppColors.primary.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Text(title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
          const SizedBox(height: 4),
          Text(subtitle, style: TextStyle(fontSize: 13, color: Colors.white.withOpacity(0.8))),
        ],
      ),
    );
  }

  Widget _sectionTitle(BuildContext context, String text) {
    return Padding(
      padding: const EdgeInsets.only(top: 24, bottom: 10),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 17,
          fontWeight: FontWeight.w700,
          color: AppColors.primary,
        ),
      ),
    );
  }

  Widget _subtitle(BuildContext context, String text) {
    return Padding(
      padding: const EdgeInsets.only(top: 14, bottom: 8),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.w600,
          color: AppColors.primary.withOpacity(0.85),
        ),
      ),
    );
  }

  Widget _paragraph(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Text(text, style: const TextStyle(fontSize: 14, height: 1.7)),
    );
  }

  Widget _bulletList(List<String> items) {
    return Padding(
      padding: const EdgeInsets.only(left: 8, bottom: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: items
            .map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('  •  ', style: TextStyle(fontSize: 14, color: AppColors.primary)),
                      Expanded(child: Text(item, style: const TextStyle(fontSize: 14, height: 1.5))),
                    ],
                  ),
                ))
            .toList(),
      ),
    );
  }

  Widget _highlightBox(String text, bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
        color: isDark ? AppColors.primary.withOpacity(0.15) : AppColors.primary.withOpacity(0.08),
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(8),
          bottomRight: Radius.circular(8),
        ),
        border: Border(left: BorderSide(color: AppColors.primary, width: 4)),
      ),
      child: Text(text, style: const TextStyle(fontSize: 13.5, height: 1.6)),
    );
  }

  Widget _dataTable(bool isDark) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
        border: Border.all(color: isDark ? Colors.white24 : Colors.black12),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          _tableRow('Ma\'lumot turi', 'Maqsad', isHeader: true, isDark: isDark),
          _tableRow('Ism', 'Murojaat egasini aniqlash', isDark: isDark),
          _tableRow('Telefon raqam', 'Aloqa o\'rnatish', isDark: isDark),
          _tableRow('Fikr matni', 'Ilovani yaxshilash', isDark: isDark, isLast: true),
        ],
      ),
    );
  }

  Widget _tableRow(String col1, String col2, {bool isHeader = false, bool isLast = false, required bool isDark}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isHeader
            ? (isDark ? AppColors.primary.withOpacity(0.2) : AppColors.primary.withOpacity(0.1))
            : null,
        border: isLast ? null : Border(bottom: BorderSide(color: isDark ? Colors.white12 : Colors.black12)),
        borderRadius: isHeader
            ? const BorderRadius.only(topLeft: Radius.circular(11), topRight: Radius.circular(11))
            : null,
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(col1, style: TextStyle(
              fontSize: 13,
              fontWeight: isHeader ? FontWeight.w600 : FontWeight.normal,
              color: isHeader ? AppColors.primary : null,
            )),
          ),
          Expanded(
            child: Text(col2, style: TextStyle(
              fontSize: 13,
              fontWeight: isHeader ? FontWeight.w600 : FontWeight.normal,
              color: isHeader ? AppColors.primary : null,
            )),
          ),
        ],
      ),
    );
  }

  Widget _contactInfo(bool isDark) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
        border: Border.all(color: isDark ? Colors.white24 : Colors.black12),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          _tableRow('Kompaniya', 'MYSTAR MChJ', isHeader: true, isDark: isDark),
          _tableRow('Email', 'shohruxbekaralov@gmail.com', isDark: isDark),
          _tableRow('Ilova', 'Muallimi Soniy', isDark: isDark, isLast: true),
        ],
      ),
    );
  }

  Widget _appInfoTable(bool isDark) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        border: Border.all(color: isDark ? Colors.white24 : Colors.black12),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          _tableRow('Ilova nomi', 'Muallimi Soniy', isHeader: true, isDark: isDark),
          _tableRow('Versiya', '1.0.0', isDark: isDark),
          _tableRow('Dasturchi', 'MYSTAR MChJ (CodingTech.uz)', isDark: isDark),
          _tableRow('Kategoriya', 'Ta\'lim (Education)', isDark: isDark),
          _tableRow('Narx', 'Bepul', isDark: isDark),
          _tableRow('Litsenziya', 'CC BY-NC 4.0 (Open Source)', isDark: isDark, isLast: true),
        ],
      ),
    );
  }

  Widget _publishInfoTable(bool isDark) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
        border: Border.all(color: isDark ? Colors.white24 : Colors.black12),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          _tableRow('Asl muallif', 'Ahmad Xodiy Maqsudiy', isHeader: true, isDark: isDark),
          _tableRow('Nashr asosi', 'VazMahkama, 3438-son, 2014', isDark: isDark),
          _tableRow('Audio', 'Jahongir qori Nematov', isDark: isDark),
          _tableRow('Raqamlashtirish', 'MYSTAR MChJ', isDark: isDark),
          _tableRow('Nashr yili', '2026', isDark: isDark, isLast: true),
        ],
      ),
    );
  }

  Widget _techBadges(bool isDark) {
    final techs = ['Flutter', 'Dart', 'FastAPI', 'Python', 'PostgreSQL', 'Redis', 'Docker'];
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: techs.map((t) => Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: isDark ? AppColors.primary.withOpacity(0.2) : AppColors.primary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(t, style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: AppColors.primary,
          )),
        )).toList(),
      ),
    );
  }

  Widget _footer(String text, bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: isDark ? Colors.white12 : Colors.black12)),
      ),
      child: Text(
        text,
        textAlign: TextAlign.center,
        style: TextStyle(fontSize: 12, color: isDark ? Colors.white38 : Colors.black38),
      ),
    );
  }
}
