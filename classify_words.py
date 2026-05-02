#!/usr/bin/env python3
"""
Word analysis for Yunus Emre Divan.
Builds a histogram of all words, classifies them as SKIP (common Turkish) 
or NEEDS_TOOLTIP (archaic/Arabic/Persian needing explanation).

The SKIP set grows iteratively — add words here as you confirm they're common.
Output: prints remaining unclassified words for review.
"""
import json, re
from collections import Counter

with open('data/divan.json', 'r', encoding='utf-8') as f:
    divan = json.load(f)
with open('data/divan_annotated.json', 'r', encoding='utf-8') as f:
    ann = json.load(f)

# Build word frequency
word_freq = Counter()
for p in divan['şiirler']:
    for b in p['beyitler']:
        for w in re.findall(r"[\w'âîûçşğöüÂÎÛÇŞĞÖÜ\-]+", b['metin'].lower()):
            if len(w) > 2:
                word_freq[w] += 1

# Already annotated
annotated = set()
for p in ann['şiirler']:
    for b in p['beyitler']:
        for w in b.get('anlamlar', {}):
            annotated.add(w)

# ============================================================
# SKIP SET: Words any modern Turkish speaker understands
# Grow this list iteratively. Once a word is here, it won't get a tooltip.
# ============================================================
SKIP = {
    # --- pronouns, particles, conjunctions, postpositions ---
    'bir','ben','sen','biz','siz','kim','ile','hem','her','var','yok',
    'iki','üç','dört','beş','altı','yedi','sekiz','dokuz','on','yüz','bin',
    'için','içün','gibi','bile','yine','gine','dahi','dahı',
    'ise','iken','imiş','idi','imdi','amma','ammâ','lâkin',
    'sana','bana','beni','seni','anı','bunda','anda','kanda',
    'anun','bunun','senün','benüm','bizüm','sizün',
    'bize','size','bizi','sizi','onlar','bunlar','şunlar',
    'kime','niye','neye','neden','nasıl','nice','niçe',
    'şöyle','böyle','öyle','nere','bura','ora',
    'mısın','misin','musun','müsün','mıdur','midür',
    'durur','dir','dür','dır','dur',
    # --- common adj/adv ---
    'çok','az','hoş','güzel','kötü','iyi','doğru','büyük','küçük',
    'ulu','kara','uzun','kısa','yeni','eski','katı','çoğu',
    'bugün','yarın','dün','şimdi','sonra','önce','evvel',
    'yakın','uzak','ırak','yüce','alçak',
    'gerçek','girçek','doğru','togrı','düz',
    'gizli','gizlü','açık','aydın',
    'güzel','çirkin','temiz','kirli',
    'henüz','hâlâ',
    # --- common nouns (any Turk knows) ---
    'haber','yol','ev','su','taş','dağ','deniz','toprak','gök','yer',
    'gün','gece','ay','yıl','baş','göz','el','dil','söz','yüz',
    'can','cân','ten','beden','ruh','kalp','akıl','akl',
    'ölüm','hayat','ömür','dünya','dünyâ','dünye',
    'allah','allâh','hak','hakk','tanrı',
    'sultan','sultân','şah','padişah',
    'dost','sevgi','aşk','ışk',
    'kişi','insan','adam','kimse','kimsene','kimesne',
    'dert','derd','gam','keder',
    'ilim','ilm','din','iman','îmân','namaz','namâz','oruç',
    'cennet','cehennem',
    'âlem','alem','cihân','cihan',
    'âdem','adem','zamân','zaman',
    'dermân','derman','karâr','karar','tamâm','tamam',
    'kudret','hikmet','rahmet',
    'kul','od','ateş','hava',
    'kuş','balık','at','deve','it',
    'kapı','köy','şehir','mülk',
    'ad','isim','ses','renk',
    'iş','güç','kuvvet',
    'sır','sırr','halk','halka',
    'kül','kan','aş','ekmek',
    'nehir','ırmak','göl','bağ','bahçe',
    'ova','çöl','gönül','gönl','ciğer','bağır',
    'nûr','nur','selâm','selam',
    'sevgü','sevgi','kabûl','kabul',
    'şükür','şükr','mâl','mal',
    'seher','düşmân','düşman',
    'nişân','nişan','kurbân','kurban',
    'nesne','ömr','vakit','saat',
    'varlık','yokluk','birlik',
    'gündüz','sabah','akşam',
    'zindân','zindan','dükkân','dükkan',
    'hükm','hüküm',
    'cevâb','cevap',
    'nasîb','nasip',
    'dâim','daim',
    'câhil','cahil',
    'mahrûm','mahrum',
    'ezelî','ebedî',
    'şer','hayır',
    'şeker','şeytân','şeytan',
    'müslüman','müsülmân',
    'hayvan','hayvân',
    'sabr','sabır',
    'hâl','hal',
    # --- proper nouns ---
    'yûnus','emre','muhammed','tapduk','hazret',
    # --- meter fragments ---
    'müstef','mefâ','îlün','ilün','ûlün','ilâtün','fe','rifet',
    # --- common verbs (all forms a Turk understands) ---
    'gel','git','ver','vir','al','bul','kal','bil','gör','dur','tur',
    'kıl','et','it','eyle','de','di','ye','iç','yaz','oku','okı',
    'çık','gir','geç','düş','at','tut','sat','kes','aç','yap','bak',
    'sor','sev','öl','doğ','yaşa','ağla','gül','sus','dinle','bekle',
    'iste','san','say','dön','bırak','koy','koş','yürü','otur','kalk',
    'yat','kaç','sakla','göster','anla','tanı','seç','başla','düşün',
    'söyle','ara','ulaş','bat','yan','sön','duy','sun','var',
    'sar','bağla','çöz','kapa','ört','giy','çek','sür','taşı',
    'ide','eyde','eyit','dile','döne',
    'yak','dol','tol','bol','don','ton',
    'ur','vur','kur','boz','aş',
    'yara','yarat','ko','kod',
    'sakın','kal','doğ','öl',
    'dön','geç','düş','bin','çık','in','koş',
    'özen','utan','kork','sevin','üz','acı',
    # --- conjugated forms (common, any Turk gets it) ---
    'olan','ola','olam','olur','olmaz','oldu','oldı','olsa','olmuş','olsun',
    'olmış','olmadı','olmaya','olıcak','olısar','olasın','olayın','olduk',
    'oluban','olupdur','olma','olgıl','olmak','olursa',
    'geldi','geldüm','geldim','gelür','gelir','gelmez','gelsün','gelsin',
    'gele','gelen','gelem','gelün','gelmedin',
    'gitdi','gitti','gider','gitmez','gitsin','giden','gide',
    'verdi','virdi','verir','virür','versin','vire','viren','virmez','virdüm','virdük',
    'aldı','alır','alur','almaz','alan',
    'buldu','buldum','buldı','bulduk','bulur','bulmaz','bulasın',
    'kaldı','kalır','kalmaz','kalur','kalmadı','kalma','kala','kalan',
    'bildi','bildüm','bilür','bilir','bilmez','bilmezem','bilürsin','bilün','bilen','bilgil',
    'gördüm','gördi','görür','görmez','gören','göresin','görelüm','görün','göre',
    'kıldı','kılur','kılar','kılan','kılam','kılmaz','kıldum','kılursın','kıla',
    'eder','ider','eyler','eyledi','eyleyem','eylegil','eylemez','eyleyen','eyledüm',
    'idüp','idüm','idem','idelüm','iden','itmez','itdi',
    'durur','turur',
    'olup','gelüp','gelip','gidüp','gidip','görüp','bilüp','oldum','koyup','varup',
    'söyler','söyle','söyleyen',
    'sever','sevdi','sevin',
    'düşdi','düşer','düşe',
    'geçer','geçdi','geçdüm','gerekse',
    'didi','dedi','diyen','diye','diyü','diyem','dimiş',
    'varam','varur','vardı','varısa',
    'gelen','gören','gele','viren',
    'benem','benümdür','sensin',
    'nedür','vardur','yokdur','budur','oldur','kimdür','gerekdür','çokdur',
    'yanar','döner','gezer','akar','biter','diler','ölmez',
    'tutdum','tutdı','tuta',
    'urdı','ura',
    'yaratdı','indi','döndi',
    'yüriyem','çıkam','gidelüm',
    'dirisen',
    # --- suffixed nouns (common root + suffix) ---
    'gönlüm','gönlün','gönli','gönüle','gönülde','gönlümi','gönüllerde',
    'gözi','göze','gözüm','gözün','gözüni','gözin',
    'başı','başın','başına','başa',
    'eli','elden','elüm','elinden','ele','elin',
    'yola','yolına','yolun','yolda','yolından','yolı','yolında','yoldan','yolum',
    'sözi','sözüm','sözün','sözini','sözin','sözleri',
    'canı','cânı','câna','canım','cânumı','cânun','cânın','cânlara','cânuma',
    'yüzi','yüzün','yüzüm','yüzin','yüzini','yüzinde','yüzinden',
    'dili','dilüm','dilün','dilde',
    'işi','işüm','işün','işe','işler',
    'odı','odına','oda',
    'güni','evi','eve',
    'sultânı','âleme','cihânda','cihâna',
    'erenlere','erenlerün',
    'dervîşlerün','âşıklarun','âşıklara','âşıkun','âşıkısan','âşıka',
    'kişiye','kimseye',
    'mülke','derde','göge','denize','denizine',
    'topraga','halka','kula','kapusında',
    'nefsün','adı','adum','nûrı','sırrı',
    'hâlüm','ömrüm','aklum','içüm','cigerüm',
    'varlıgı','sevgüsi','dertlü',
    'vaktinde',
    # --- misc common ---
    'gerek','degül','degil','değil','gerekmez',
    'cümle','hep','şol','çün','çünki','eger','eğer','ger','meger',
    'kendü','kendi','kendüm','kendün','kendüye','kendözin',
    'bunca','birkaç','birgün','birisi',
    'üstine','içerü','karşu','ırak',
    'sensüz','yalan','hey','bak',
    'yitmiş','yirde','yüri',
    'gice','hîç','hiç',
    'işkun','ışkun','ışka','ışkı','işka',
    'dünyâyı','dünyâya','dünyâda','dünyede','dünyâdan',
    'içinde','ana','yana','senden','dosta','yolda',
    'yidi','aceb','benzer',
    'varısa','benden','kimi','biri',
    'dostun','sundum',
    'itsün','etegin',
    'kuş','eri','ere',
    'gerçek','güle',
    'tolu','niçe','girçek',
    'kodı','yatur','togrı',
    'ögüt','delü','ayru',
    "hakk'a","hakk'ı","hakk'un","yûnus'un","yûnus'a","yûnus'ı",
    "hazret'e","çalab'um","hak'ı","arş'a","muhammed'ün",
    "uçmak'da",
    "n'eyler","n'ideyin","n'ideyüm","n'eyledi","n'eylesün",
    'dime','bundan','bunı','sende','sakın',
    'toldı','kül','eve',
    'şimden','gelem','olupdur','diyem',
    'çâre',
    'kur\'ân',
    'seher','düşmân','nişânı',
    'ilâtün',
    'sıgmaz','yagmâya',
    'kimün','bizden','olursa',
    'evliyâ','hırs','cemâlin',
    'dile','kılan','diyen','muhammed','allâh','kudret',
    'emrem','yiter','irdi',
    'irte',  # ertesi
    'biş',  # beş
    'yaşı','yavı',  # hmm yavı is archaic... remove from skip
    'kırk','arada',
    'lâyık',  # layık - common enough
    'hâzır',  # hazır - common
    'şarâbın',  # keep out of skip - archaic meaning
    'dün-gün',
    'bilün','eylegil','olgıl','kogıl',  # kogıl is archaic! remove
    'dilersen',
    'bende',
    'idüben',
    'sensün',
    'agaç',  # ağaç
    'güneş',
    'sanur',  # sanır
    'yürür',
    'sanma',
    'girmez',
    'bakan',
    'neler',
    'nite',  # nite = nasıl (archaic? borderline)
    'kalma',
    'diri',  # diri = canlı (common)
    'uçar',
    'gökden',
    'kişinün',
    'irer',  # erir/ulaşır
    'isterem',  # isterim
    'hâlin',
    'yirün',
    'yüzine',
    'âşıka',
    'dirler',  # derler
    'dünyâdan',
    'geçdüm',
    'gönüllerde',
}

# Remove words that are actually archaic (shouldn't be in SKIP)
SKIP.discard('kogıl')
SKIP.discard('yavı')
SKIP.discard('şarâbın')

remaining = []
for w, f in word_freq.most_common():
    if w in annotated:
        continue
    if w in SKIP:
        continue
    if f < 5:
        continue
    remaining.append((w, f))

print(f"Remaining (freq>=5, not annotated, not skipped): {len(remaining)}")
print()
for w, f in remaining[:80]:
    print(f"  {w:30s} {f:3d}")

# Save the skip set for use in annotate.py
with open('data/skip_words.json', 'w', encoding='utf-8') as f:
    json.dump(sorted(SKIP), f, ensure_ascii=False, indent=2)
print(f"\n✓ Saved {len(SKIP)} skip words to data/skip_words.json")
