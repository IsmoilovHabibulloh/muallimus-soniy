-- Update letter header units with positional forms
-- Run inside postgres container:
--   docker exec -i muallimus-soniy-postgres-1 psql -U muallimus -d muallimus_soniy < update_headers.sql

-- Connecting letters: beginning form + tatweel + fatha, tatweel + middle form + tatweel + kasra, tatweel + end form + damma
-- Non-connecting letters (ز,د,ذ,و): beginning = isolated, middle/end = tatweel + letter

-- Page 4
UPDATE text_units SET text_content = 'زَ ـزِ ـزُ' WHERE text_content = 'زَ زِ زُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'مـَ ـمـِ ـمُ' WHERE text_content = 'مَ مِ مُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'تـَ ـتـِ ـتُ' WHERE text_content = 'تَ تِ تُ' AND metadata::text LIKE '%_header%';

-- Page 5
UPDATE text_units SET text_content = 'نـَ ـنـِ ـنُ' WHERE text_content = 'نَ نِ نُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'يـَ ـيـِ ـيُ' WHERE text_content = 'يَ يِ يُ' AND metadata::text LIKE '%_header%';

-- Page 6
UPDATE text_units SET text_content = 'بـَ ـبـِ ـبُ' WHERE text_content = 'بَ بِ بُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'كـَ ـكـِ ـكُ' WHERE text_content = 'كَ كِ كُ' AND metadata::text LIKE '%_header%';

-- Page 7
UPDATE text_units SET text_content = 'لـَ ـلـِ ـلُ' WHERE text_content = 'لَ لِ لُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'وَ ـوِ ـوُ' WHERE text_content = 'وَ وِ وُ' AND metadata::text LIKE '%_header%';

-- Page 8
UPDATE text_units SET text_content = 'هـَ ـهـِ ـهُ' WHERE text_content = 'هَ هِ هُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'فـَ ـفـِ ـفُ' WHERE text_content = 'فَ فِ فُ' AND metadata::text LIKE '%_header%';

-- Page 9
UPDATE text_units SET text_content = 'قـَ ـقـِ ـقُ' WHERE text_content = 'قَ قِ قُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'شـَ ـشـِ ـشُ' WHERE text_content = 'شَ شِ شُ' AND metadata::text LIKE '%_header%';

-- Page 10
UPDATE text_units SET text_content = 'سـَ ـسـِ ـسُ' WHERE text_content = 'سَ سِ سُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'ثـَ ـثـِ ـثُ' WHERE text_content = 'ثَ ثِ ثُ' AND metadata::text LIKE '%_header%';

-- Page 11
UPDATE text_units SET text_content = 'صـَ ـصـِ ـصُ' WHERE text_content = 'صَ صِ صُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'طـَ ـطـِ ـطُ' WHERE text_content = 'طَ طِ طُ' AND metadata::text LIKE '%_header%';

-- Page 12
UPDATE text_units SET text_content = 'جـَ ـجـِ ـجُ' WHERE text_content = 'جَ جِ جُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'خـَ ـخـِ ـخُ' WHERE text_content = 'خَ خِ خُ' AND metadata::text LIKE '%_header%';

-- Page 13
UPDATE text_units SET text_content = 'حـَ ـحـِ ـحُ' WHERE text_content = 'حَ حِ حُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'غـَ ـغـِ ـغُ' WHERE text_content = 'غَ غِ غُ' AND metadata::text LIKE '%_header%';

-- Page 14
UPDATE text_units SET text_content = 'عـَ ـعـِ ـعُ' WHERE text_content = 'عَ عِ عُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'دَ ـدِ ـدُ' WHERE text_content = 'دَ دِ دُ' AND metadata::text LIKE '%_header%';

-- Page 15
UPDATE text_units SET text_content = 'ضـَ ـضـِ ـضُ' WHERE text_content = 'ضَ ضِ ضُ' AND metadata::text LIKE '%_header%';
UPDATE text_units SET text_content = 'ذَ ـذِ ـذُ' WHERE text_content = 'ذَ ذِ ذُ' AND metadata::text LIKE '%_header%';

-- Page 16
UPDATE text_units SET text_content = 'ظـَ ـظـِ ـظُ' WHERE text_content = 'ظَ ظِ ظُ' AND metadata::text LIKE '%_header%';
