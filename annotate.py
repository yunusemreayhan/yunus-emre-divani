#!/usr/bin/env python3
"""
Annotate Divan poems with word meanings and modern Turkish translations.
Uses the glossary for known words and generates contextual meanings.
"""
import json, re, os

def load_data():
    with open('data/divan.json', 'r', encoding='utf-8') as f:
        divan = json.load(f)
    with open('data/sozluk.json', 'r', encoding='utf-8') as f:
        sozluk = json.load(f)
    return divan, sozluk

def normalize(word):
    """Normalize a word for glossary lookup."""
    w = word.lower().strip("'\".,;:!?()-–")
    w = w.replace("'", "")  # remove mid-word apostrophes too
    return w

def shorten(meaning):
    """Get short version of a meaning. Resolve Bkz. references."""
    if meaning.startswith('Bkz.') or meaning.startswith('Bkz '):
        return None  # Skip, will be caught by EXTRA_MEANINGS or direct lookup
    short = meaning.split('.')[0] if '.' in meaning else meaning
    if len(short) > 60:
        short = short.split(',')[0]
    if len(short) > 80:
        short = short[:77] + '...'
    return short.strip() if short.strip() else None

# Additional meanings not in the glossary or commonly needed
EXTRA_MEANINGS = {
    'ışk': 'Aşk, ilahi sevgi',
    'aşk': 'Aşk, ilahi sevgi',
    'gönül': 'Kalp, yürek, iç dünya',
    'cân': 'Can, ruh, hayat',
    'cânum': 'Canım, ruhum',
    'dost': 'Sevgili, Allah, mürşid',
    'dostı': 'Sevgili, Allah, mürşid',
    'âşık': 'Seven, Allah aşığı',
    'ma\'şûk': 'Sevgili, Allah',
    'ma\'şûka': 'Sevgili, Allah',
    'uçmak': 'Cennet',
    'uçmag': 'Cennet',
    'tamu': 'Cehennem',
    'miskîn': 'Yoksul, alçakgönüllü, benliksiz',
    'dervîş': 'Yoksul, tarikat ehli, Allah yolcusu',
    'hak': 'Allah, gerçek, doğru',
    'hakk': 'Allah, gerçek',
    'çalap': 'Tanrı, Allah',
    'tapduk': 'Yunus Emre\'nin şeyhi',
    'visâl': 'Kavuşma, vuslat',
    'firâk': 'Ayrılık',
    'zevâl': 'Son, yok oluş',
    'bekâ': 'Sonsuzluk, kalıcılık',
    'fenâ': 'Yokluk, geçicilik, dünya',
    'ezel': 'Başlangıçsız geçmiş, öncesizlik',
    'ebed': 'Sonsuz gelecek',
    'tevhîd': 'Birlik, Allah\'ın birliği',
    'vahdet': 'Birlik, teklik',
    'kesret': 'Çokluk, çeşitlilik',
    'nûr': 'Işık, aydınlık',
    'sûret': 'Şekil, dış görünüş, beden',
    'ma\'nî': 'Anlam, iç yüz, gerçek',
    'ma\'rifet': 'Allah bilgisi, irfan',
    'hikmet': 'Gizli sebep, bilgelik',
    'şerî\'at': 'Dinin zahiri kuralları',
    'tarîkat': 'Tasavvuf yolu',
    'hakîkat': 'Gerçek, öz',
    'ledün': 'İlahi sır bilgisi',
    'tecellî': 'Allah\'ın görünmesi, belirmesi',
    'müşâhade': 'İlahi alemi görme',
    'seyr': 'Manevi yolculuk',
    'sülûk': 'Tarikat yolculuğu',
    'mürşid': 'Yol gösteren şeyh',
    'mürîd': 'Tarikata giren kişi',
    'zühd': 'Dünyadan el çekme, ibadet',
    'tâ\'at': 'İbadet, kulluk',
    'münâcât': 'Allah\'a yakarış, dua',
    'cemâl': 'Güzellik, yüz güzelliği',
    'celâl': 'Büyüklük, ululuk',
    'kevser': 'Cennet ırmağı',
    'sâkî': 'Kadeh sunan, mürşid',
    'meyhâne': 'Tekke, mürşidin gönlü',
    'şarâb': 'İlahi aşk, irfan',
    'kadeh': 'İlahi aşk kadehi',
    'esrük': 'Sarhoş, aşk sarhoşu',
    'mest': 'Sarhoş, kendinden geçmiş',
    'bülbül': 'Aşık, derviş',
    'gül': 'Sevgili, güzellik',
    'gülistân': 'Gül bahçesi, cennet',
    'vîrân': 'Yıkık, harap',
    'genc': 'Hazine, define',
    'gevher': 'Mücevher, değerli öz',
    'kân': 'Maden ocağı, kaynak',
    'bahrî': 'Denizci, dalgıç',
    'gavvâs': 'Dalgıç, inci arayan',
    'pervâne': 'Işığa koşan kelebek, aşık',
    'mansûr': 'Hallac-ı Mansur, aşk şehidi',
    'mecnûn': 'Deli, aşk delisi',
    'leylî': 'Sevgili (Leyla)',
    'ferhâd': 'Aşk kahramanı, fedakar aşık',
    'iblîs': 'Şeytan',
    'nefs': 'Benlik, ego',
    'arş': 'En yüce gök, Allah\'ın makamı',
    'ferş': 'Yeryüzü',
    'mi\'râc': 'Hz. Peygamber\'in göğe yükselişi',
    'kıyâmet': 'Dünyanın sonu, diriliş günü',
    'kamu': 'Bütün, hep, herkes',
    'kamusı': 'Hepsi, tamamı',
    'kamudan': 'Herkesten, hepsinden',
    'bura': 'Büker, eğer (boyun burmak)',
    'ırar': 'Uzaklaştırır, koparır',
    'tolar': 'Dolar, dolu olur',
    'tura': 'Durur, ayakta kalır',
    'yire': 'Yere',
    'yiri': 'Yeri',
    'ayruk': 'Başka, artık, gayrı',
    'niçün': 'Niçin, neden',
    'kanı': 'Hani, nerede',
    'n\'iderse': 'Ne ederse, ne yaparsa',
    'n\'ider': 'Ne eder, ne yapar',
    'n\'ola': 'Ne olur',
    'n\'eyler': 'Ne eyler, ne yapar',
    'n\'idelüm': 'Ne edelim',
    'dirlik': 'Yaşayış, hayat',
    'dirilmek': 'Yaşamak, hayat sürmek',
    'girü': 'Geri, tekrar',
    'uş': 'İşte',
    'dahı': 'Dahi, de, bile, hem',
    'eyü': 'İyi, güzel',
    'yavuz': 'Kötü, fena',
    'yigrek': 'Daha iyi, üstün',
    'bellü': 'Belli, açık',
    'bezirgân': 'Tüccar, tacir',
    'bâzirgân': 'Tüccar, tacir',
    'zinhâr': 'Sakın, asla, aman',
    'çava': 'İklim, memleket, uzak yer',
    'nüvaht': 'Okşama, çalgı çalma',
    'nühavht': 'Okşama, çalgı çalma',
    'hânumân': 'Ev, bark, ocak',
    'hânumânı': 'Ev, bark, ocak',
    'hânmân': 'Ev, bark, ocak',
    'ög': 'Akıl, hatır, zihin',
    'öginden': 'Aklından, zihninden',
    'ögüme': 'Aklıma, zihnime',
    'ögüni': 'Aklını, zihnini',
    'ögin': 'Aklını, zihnini',
    'özge': 'Başka, gayrı, farklı',
    'özgeyi': 'Başkasını, gayrısını',
    'da\'vî': 'İddia, dava',
    'da\'vîden': 'İddiadan, davadan',
    'da\'vîsin': 'İddiasını, davasını',
    'da\'vî kılmak': 'İddia etmek',
    'sebük': 'Hafif, değersiz, önemsiz',
    'sebüksal': 'Hafif, önemsiz, değersiz',
    'peşimân': 'Pişman',
    'peşimâna': 'Pişmanlığa',
    'pişmân': 'Pişman',
    'assı': 'Fayda, menfaat, kazanç',
    'yuyucı': 'Yıkayıcı (ölü yıkayan)',
    'koyucı': 'Koyan, yerleştiren',
    'sarıcı': 'Saran (kefen saran)',
    'iledüp': 'İletip, götürüp',
    'tana': 'Hayrete, şaşkınlığa (tana kalmak: şaşmak)',
    'görnem': 'Göreyim, göstereyim',
    'didi': 'Dedi',
    'ündür': 'Sestir, nidadır',
    'dügündür': 'Düğündür, bayramdır',
    'dîndür': 'Dindir, inançtır',
    'öndin': 'Önce, evvel',
    'ulaşalıdan': 'Ulaşalıdan beri, kavuştuğundan beri',
    'va\'deyledi': 'Vaad etti, söz verdi',
    'sevindügi': 'Sevindiği',
    'ırılmayam': 'Ayrılmayım',
    'sürülmeyem': 'Sürülmeyeyim, kovulmayayım',
    'dimeyem': 'Demeyeyim, söylemeyeyim',
    'irmez': 'Erişmez, ulaşmaz',
    'idindi': 'Edindi, kabul etti',
    'sorarısan': 'Sorarsan, soracak olursan',
    'kimesne': 'Kimse, hiç kimse',
    'kimesneye': 'Kimseye, hiç kimseye',
    'dergâh': 'Tekke, Allah\'ın huzuru',
    'âşıkan': 'Ey âşıklar (hitap)',
    'mezheb': 'Yol, din yolu',
    'yarınum': 'Yarınım',
    'viribidi': 'Verdi, bıraktı',
    'ârâyiş': 'Süs, bezek, ziynet',
    'eydür': 'Der, söyler',
    'eydur': 'Der, söyler',
    'eyitdi': 'Söyledi, dedi',
    'eyit': 'Söyle, de',
    'eyitmesün': 'Söylemesin, demesin',
    'eyitdiler': 'Söylediler, dediler',
    'eydürem': 'Derim, söylerim',
    'düte': 'Tüte, yana, yanar',
    'sünük': 'Kemik',
    'ırıla': 'Ayrıla, kopup gitsin',
    'ırılmak': 'Ayrılmak, uzaklaşmak',
    'yazuk': 'Günah, suç',
    'yazuklarumuz': 'Günahlarımız',
    'agu': 'Zehir',
    'agusı': 'Zehiri',
    'tiryâk': 'Panzehir, ilaç',
    'renc': 'Zahmet, eziyet, dert',
    'rencümi': 'Zahmetimi, derdimi',
    'perrân': 'Uçan, uçarak',
    'efgân': 'Feryat, ağlayıp bağırma',
    'biryân': 'Kebap, kızarmış, yanmış',
    'bişe': 'Pişe, yana',
    'ditrer': 'Titrer',
    'korkubanı': 'Korkarak',
    'tartıla': 'Tartılır, ölçülür',
    'yırtıla': 'Yırtılır, açılır',
    'heybetinden': 'Korkunçluğundan, azametinden',
    'çerâk': 'Mum, ışık, kandil',
    'çerâg': 'Mum, ışık, kandil',
    'kandîl': 'Kandil, ışık',
    'aydın': 'Aydınlık, parlak',
    'karanular': 'Karanlıklar',
    'şâd': 'Sevinçli, mutlu',
    'şâdıyam': 'Sevinçliyim, mutluyum',
    'şâdılık': 'Sevinç, mutluluk',
    'ton': 'Elbise, giysi',
    'tonını': 'Elbisesini, giysisini',
    'tonı': 'Elbisesi, giysisi',
    'tonın': 'Elbisesini',
    'tonları': 'Elbiseleri',
    'dîdâr': 'Yüz, Allah\'ın cemali, vuslat',
    'münkir': 'İnkarcı, inanmayan',
    'münkirisen': 'İnkarcısın, inanmıyorsun',
    'müselmân': 'Müslüman',
    'müselmânam': 'Müslümanım',
    'fermân': 'Emir, buyruk',
    'fermânam': 'Emrine uyarım, buyruğundayım',
    'fâyide': 'Fayda',
    'dutmazısa': 'Tutmazsa, uymazsa',
    'bınar': 'Pınar, kaynak, gözyaşı kaynağı',
    'ferîdûn': 'Efsanevi İran hükümdarı, adalet ve zenginlik sembolü',
    'nûşirevân': 'Adaletiyle ünlü eski İran hükümdarı',
    'kârûn': 'Musa devrinde yaşayan, zenginliğiyle mağrur olup yere batan kişi',
    'nemrûd': 'İbrahim Peygamber\'i ateşe atan zalim hükümdar',
    'süleymân': 'Hem peygamber hem hükümdar, kuş dili bilen, cinlere hükmeden',
    'şeddâd': 'Cennet benzeri bahçe yaptıran, tanrılık iddia eden hükümdar',
    'fir\'avn': 'Musa Peygamber çağında tanrılık iddia eden Mısır hükümdarı',
    'firavn': 'Musa Peygamber çağında tanrılık iddia eden Mısır hükümdarı',
    'hâmân': 'Firavun\'un veziri',
    'ibrâhîm': 'Ateşe atılıp yanmayan peygamber, tevhid dininin babası',
    'ismâîl': 'İbrahim\'in oğlu, kurban edilmek istenen peygamber',
    'ya\'kûb': 'Yusuf\'un babası, hasretle ağlayan peygamber',
    'yûsuf': 'Güzelliğiyle ünlü peygamber, kuyuya atılan, Mısır sultanı olan',
    'eyyûb': 'Sabır sembolü peygamber',
    'zekeriyyâ': 'Testereyle biçilen peygamber',
    'idrîs': 'Terzilerin piri olan peygamber',
    'hızır': 'Ölümsüzlük suyu içen, darda kalanlara yardım eden',
    'ilyâs': 'Hızır ile birlikte anılan, denizde yardım eden peygamber',
    'belkîs': 'Saba melikesi, Süleyman\'ın daveti ile iman eden',
    'edhem': 'İbrahim Edhem, tahtını terk eden sufi hükümdar',
    'bâyezîd': 'Bayezid-i Bistami, büyük sufi',
    'cüneyd': 'Cüneyd-i Bağdadi, tasavvuf büyüğü',
    'yaraklanup': 'Hazırlanıp, yol azığını alıp',
    'ansuzın': 'Ansızın, birdenbire, habersizce',
    'ferseng': 'Fersah, uzun mesafe (yaklaşık 6 km)',
    'fersenge': 'Fersaha, uzun mesafeye',
    'bigi': 'Gibi, benzer',
    'talbınma': 'Çırpınma, çabalama',
    'talbınmak': 'Çırpınmak, sıçramak',
    'döymez': 'Dayanamaz, tahammül edemez',
    'döymek': 'Dayanmak, tahammül etmek',
    # --- Words from classification analysis (freq>=5, genuinely archaic) ---
    'ıyân': 'Aşikar, açık, belli',
    'âhir': 'Son, nihayet, sonunda',
    'kayusı': 'Kaygısı, endişesi',
    'ârif': 'Bilen, irfan sahibi, Allah\'ı tanıyan',
    'ârifler': 'İrfan sahipleri, bilenler',
    'kogıl': 'Bırak, koy (emir kipi)',
    'zîrâ': 'Çünkü, zira',
    'cevlân': 'Dolaşma, dönme, seyir',
    'ıssı': 'Sahibi, iye',
    'yavı': 'Kayıp, yitik',
    'terkin': 'Terkini, vazgeçmesini',
    'tama': 'Tamah, açgözlülük, hırs',
    'tama\'': 'Tamah, açgözlülük, hırs',
    'seyrân': 'Gezinti, seyir, temaşa',
    'acâyib': 'Acayip, şaşılacak, tuhaf',
    'kullık': 'Kulluk, kölelik, ibadet',
    'kulluk': 'Kulluk, kölelik, ibadet',
    'nendür': 'Nedir, ne şeydir',
    'kasd': 'Kasıt, niyet, maksat',
    'su\'âl': 'Sual, soru',
    'harâb': 'Harap, yıkık, perişan',
    'meydân': 'Meydan, alan, ortaya çıkma yeri',
    'yarak': 'Hazırlık, silah, azık',
    'bâzâr': 'Pazar, çarşı, alışveriş',
    'beyân': 'Açıklama, bildirme, ifade',
    'şûk': 'Neşe, sevinç, coşku',
    'arzû': 'Arzu, istek, özlem',
    'dutgıl': 'Tut (emir), yapış, sarıl',
    'hâcet': 'İhtiyaç, gereklilik, dilek',
    'fidî': 'Feda, kurban',
    'belâ': 'Bela, sıkıntı, musibet',
    'esîr': 'Esir, tutsak, bağımlı',
    'cefâ': 'Eziyet, sıkıntı, zulüm',
    'kanâ': 'Kana (kan+a), kana boyandı',
    'tuyan': 'Duyan, hisseden',
    'hâs': 'Has, özel, seçkin',
    'izzet': 'Şeref, onur, yücelik',
    'âkıbet': 'Sonuç, son, akıbet',
    'inen': 'Çok, pek, gayet',
    'mahabbet': 'Muhabbet, sevgi, sohbet',
    'vücûd': 'Vücut, beden, varlık',
    'küfr': 'Küfür, inkar, nankörlük',
    'esenledüm': 'Selamladım, veda ettim',
    'âkıl': 'Akıllı, bilge',
    'dâr': 'Ev, yurt, mekan; darağacı',
    'safâ': 'Gönül temizliği, huzur, neşe',
    'sâfî': 'Saf, temiz, katıksız',
    'tâlib': 'Talip, isteyen, arayan',
    'vâsıl': 'Ulaşan, kavuşan, eren',
    'zâhid': 'Zahit, dünyadan el çeken, sofu',
    'bülbülcügüm': 'Bülbülcüğüm (sevgi hitabı)',
    'şarâb': 'Şarap, ilahi aşk şarabı',
    'şarâbın': 'Şarabını, ilahi aşk şarabını',
    'kâfir': 'İnkarcı, nankör',
    'mü\'min': 'İnanan, iman sahibi',
    'münâfık': 'İki yüzlü, riyakar',
    'riyâ': 'Gösteriş, ikiyüzlülük',
    'kanâ\'at': 'Kanaat, yetinme, az ile razı olma',
    'halîl': 'Dost, İbrahim Peygamber\'in lakabı',
    'habîb': 'Sevgili, Hz. Muhammed\'in lakabı',
    'vahdet': 'Birlik, teklik (tasavvuf)',
    'kesret': 'Çokluk, çeşitlilik',
    'fenâ': 'Yokluk, geçicilik; benliğin erimesi',
    'bekâ': 'Sonsuzluk, kalıcılık',
    'sekrân': 'Sarhoş, mest',
    'hayrân': 'Hayran, şaşkın, kendinden geçmiş',
    'sultân': 'Sultan, hükümdar, manevi otorite',
    # --- Missing words from poem 5 and broader analysis ---
    'kîl': 'Dedikodu, laf (kîl ü kâl: dedikodu)',
    'kîl ü kâl': 'Dedikodu, boş laf, söz',
    'hâzır': 'Hazır, mevcut, her yerde var olan',
    'teslîm': 'Teslim, boyun eğme, bırakma',
    'hıdmet': 'Hizmet, kulluk',
    'pervâne': 'Işığa koşan kelebek, aşık',
    'sineg': 'Sinek',
    'sinegile': 'Sinekle, sinek ile',
    'âsil': 'Asil, soylu',
    'zâde': 'Oğul, evlat, soyundan gelen',
    'hisâb': 'Hesap, sayı, muhakeme',
    'halâyık': 'Yaratıklar, halk, insanlar',
    'tevbe': 'Tövbe, pişmanlık, dönüş',
    'lâhî': 'İlahi (meter fragment)',
    'âhret': 'Ahiret, öbür dünya',
    'dirligi': 'Dirliği, yaşayışı, geçimi',
    'kapuda': 'Kapıda, huzurda',
    'olurısa': 'Olursa, eğer olursa',
    'kâtil': 'Öldürücü, katil, helak edici',
    'helâl': 'Helal, dinen uygun, hak edilmiş',
    'sal': 'Bırak, sal, koyuver (emir)',
    'âsil': 'Asil, soylu, köklü',
    'zâde': 'Oğul, evlat, soyundan gelen',
    'ma\'nîsi': 'Manası, anlamı',
    'ma\'nîde': 'Manada, anlamda',
    # --- Poem 21 and broader missing words ---
    'muhtâc': 'Muhtaç, ihtiyaç sahibi',
    'karır': 'Yaşlanır, ağarır, kurur',
    'budak': 'Dal, ağaç dalı',
    'budaga': 'Dala, budağa',
    'budaklarun': 'Dallarının',
    'gügercin': 'Güvercin',
    'duraç': 'Durak, konak yeri',
    'teferrüc': 'Gezinti, seyir, ferahlama',
    'teferrüclen': 'Gezin, seyret, ferahla',
    'fuzûl': 'Gereksiz, boş, lüzumsuz',
    'fuzûllık': 'Gereksizlik, boşuna iş',
    'eksük': 'Eksik, noksan',
    'eksükligün': 'Eksikliğin, noksanın',
    'kadd': 'Boy, endam',
    'kaddün': 'Boyun, endamın',
    'sırr': 'Sır, gizli hakikat',
    'sırrıdur': 'Sırrıdır, gizli hakikatidir',
    'sırrun': 'Sırrın, gizli hakikatin',
    # Common archaic words appearing across many poems
    'latîf': 'Güzel, ince, zarif, hoş',
    'şîrîn': 'Tatlı, hoş, sevimli',
    'agaç': 'Ağaç',
    'devr': 'Dönüş, çağ, zaman',
    'kazan': 'Kazan, tencere',
    'saç': 'Saç; saçmak, dağıtmak',
    'dilek': 'İstek, arzu, dua',
    'bezenüben': 'Bezenerek, süslenerek',
    'düzünüben': 'Düzünerek, süslenerek',
    'uzanuban': 'Uzanarak, yönelerek',
    'bâkî': 'Kalıcı, sonsuz, ebedi',
    'mismil': 'Temiz, pak, arı',
    'pâs': 'Kir, pas, gönül karanlığı',
    'pâsı': 'Kiri, pası',
    'yunmak': 'Yıkanmak, temizlenmek',
    'yunmayınca': 'Yıkanmayınca, temizlenmeyince',
    'yumayınca': 'Yıkamayınca',
    'kodunısa': 'Koyduğunsa, bıraktıysan',
    'yudunısa': 'Yıkadıysan, temizlediysen',
    'ikrâr': 'İnanç, söz verme, kabul',
    'murdâr': 'Kirli, pis',
    'divşürenler': 'Toplayanlar, derleyenler',
    'himmet': 'Manevi yardım, gayret, mürşidin yardımı',
    'kîn': 'Kin, düşmanlık',
    'çagşabanı': 'Dağılarak, çürüyerek',
    'ulanı': 'Ekleneni, birleşeni',
    'ulşup': 'Ulaşıp, yapışıp',
    'yolanı': 'Yolunmuşu, soyulmuşu',
    'günehdür': 'Günahtır',
    'zârı': 'Ağlayış, inleme',
    'çatar': 'Kurar, dizer, birbirine bağlar',
    'davara': 'Davara, hayvana, mala',
    'dileni': 'Dileneni, isteyeni',
    'gövdesine': 'Bedenine, vücuduna',
    'aldanuban': 'Aldanarak, kanarak',
    'irahman': 'Rahman, Allah',
    'irahmansuzına': 'Rahmansızına, Allah\'sızına, imansızına',
    'sırât': 'Cehennem üzerindeki köprü',
    'hûrî': 'Cennet güzeli',
    # --- Archaic/Ottoman words batch 2 ---
    'kaçan': 'Ne zaman, ne vakit',
    'şâh': 'Padişah, hükümdar, sultan',
    'srâfîl': 'İsrafil (sûr üfleyecek melek)',
    'isrâfîl': 'İsrafil (sûr üfleyecek melek)',
    'lisân': 'Dil, lisan',
    'togan': 'Doğan kuşu, şahin',
    'toganla': 'Doğan kuşuyla',
    'deryâ': 'Deniz, okyanus',
    'vuslat': 'Kavuşma, sevgiliye erişme',
    'eşkere': 'Açık, aşikar, belli',
    'turak': 'Durak, makam, konak',
    'turagı': 'Durağı, makamı',
    'içre': 'İçinde, içerisinde',
    'göyner': 'Yanar, tutuşur (gönül yanması)',
    'anunçün': 'Onun için, o yüzden',
    'râhat': 'Rahat, huzur',
    'destân': 'Destan, hikaye, masal',
    'secde': 'Secde, yere kapanma',
    'gelicek': 'Gelince, geldiğinde',
    'göricek': 'Görünce, gördüğünde',
    'togan': 'Doğan kuşu, şahin',
    'togar': 'Doğar, doğuverir',
    'kapu': 'Kapı',
    'kapusı': 'Kapısı',
    'kapusın': 'Kapısını',
    'levh': 'Levh-i mahfuz, kader yazısı',
    'makâm': 'Makam, mertebe, derece',
    'makâmı': 'Makamı, mertebesi',
    'harâm': 'Haram, yasak',
    'hârâmî': 'Haydut, yol kesen',
    'cânân': 'Sevgili, can sevgili',
    'günâh': 'Günah, suç',
    'insân': 'İnsan',
    'dîvâne': 'Deli, mecnun, aşk delisi',
    'fidâ': 'Feda, kurban',
    'inâyet': 'Yardım, lütuf, ihsan',
    'âhiret': 'Ahiret, öbür dünya',
    'mahlûk': 'Yaratık, yaratılmış',
    'bahâr': 'Bahar, ilkbahar',
    'tatlu': 'Tatlı, hoş',
    'sohbet': 'Sohbet, söyleşi, muhabbet',
    'menzil': 'Konak, durak, mesafe',
    'perde': 'Perde, örtü, engel',
    'humâr': 'İçki sonrası baş ağrısı, sersemlik',
    'sâz': 'Çalgı, müzik aleti',
    'hûr': 'Cennet güzeli, huri',
    'brâhîm': 'İbrahim (peygamber)',
    'cebrâîl': 'Cebrail (vahiy meleği)',
    'dimegil': 'Deme, söyleme',
    'kendözini': 'Kendisini, kendini',
    'n\'idem': 'Ne edeyim, ne yapayım',
    'okıyan': 'Okuyan',
    'buyrugın': 'Buyruğunu, emrini',
    'getür': 'Getir',
    'erden': 'Erden, ermişten, veliden',
    'urur': 'Vurur, atar',
    'kiçi': 'Küçük',
    'dükkânı': 'Dükkanı, dünyayı (mecaz)',
    'sorgıl': 'Sor, soruver',
    'sanman': 'Sanmayın, zannetmeyin',
    'dîvâr': 'Duvar',
    'dîvârı': 'Duvarı',
    'baykuş': 'Baykuş (viranelerde öten kuş)',
    'ileyinden': 'Yanından, tarafından',
    'zir\'elinde': 'Pençesinde, tırnağında',
    'erligi': 'Erliği, yiğitliği, ermişliği',
    'erlik': 'Yiğitlik, ermişlik',
    'pîş': 'Önde, ileri, öncü',
    'kolmaşa': 'Kolayca, kolay kolay',
    'anterî': 'Hile, düzen, aldatma',
    'iven': 'Acele eden, koşan',
    'paşa': 'Paşa, büyük, ulu',
    'kulı': 'Kulu, hizmetkarı',
    'ilden': 'Elden, memleketten',
    'il': 'El, memleket, yurt',
    'degme': 'Herhangi, her, rastgele',
    'degmesinde': 'Herhangi birinde, her birinde',
    'belürmez': 'Belirmez, görünmez',
    'âlimler': 'Alimler, bilginler',
    'neyimiş': 'Ne imiş, neymiş',
    'şûka': 'Neşeye, sevince',
    'bülbülem': 'Bülbülüm, aşık gibi inlerim',
    'râzumı': 'Sırrımı, gizlimi',
    'kudse': 'Kudüs\'e, kutsallığa',
    'resûla\'llâh': 'Allah\'ın elçisi, Hz. Muhammed',
    'dirligüm': 'Dirliğim, yaşayışım',
    'olmayısar': 'Olmayacak, olmaz',
    'dilerisen': 'Dilersen, istersen',
    'evvelki': 'Önceki, ilk',
    'yitdi': 'Yitti, kayboldu',
    'ma\'nîsin': 'Manasını, anlamını',
    'idük': 'İdik, imişiz',
    'olanlarun': 'Olanların',
    'halkun': 'Halkın, insanların',
    'varıdı': 'Vardı, gitti',
    'dilidür': 'Dilidir',
    'dutar': 'Tutar, yakalar',
    'komaz': 'Koymaz, bırakmaz',
    'koma': 'Koyma, bırakma',
    'kodum': 'Koydum, bıraktım',
    'didüm': 'Dedim',
    'direm': 'Derim, söylerim',
    'dâra': 'Darağacına, dara',
    'yanalum': 'Yanalım, tutuşalım',
    'aglaşalum': 'Ağlaşalım',
    'olubilsem': 'Olabilsem',
    'turdı': 'Durdu, ayakta kaldı',
    'gökde': 'Gökte',
    'gögi': 'Göğü',
    'bagrı': 'Bağrı, göğsü, yüreği',
    'olmışam': 'Olmuşum',
    'varı': 'Varı, varlığı, malı',
    'işde': 'İşte',
    'işbu': 'İşte bu, bu',
    'yâre': 'Sevgiliye, dosta',
    'sine': 'Göğüs, bağır, kalp',
}

# Compound word meanings (hyphenated terms)
COMPOUND_MEANINGS = {
    'bî-çâre': 'Çaresiz, zavallı',
    'dem-be-dem': 'An be an, sürekli',
    'ser-gerdân': 'Başı dönen, şaşkın, hayran',
    'ser-mâye': 'Sermaye, ana mal, esas',
    'ser-mâyesi': 'Sermayesi, asıl varlığı',
    'ser-te-ser': 'Baştan başa, tamamen',
    'ber-dâr': 'Asılmış, darağacında',
    'ene\'l-hak': 'Ben Hakk\'ım (Hallac-ı Mansur\'un sözü)',
    'el-hamdüli\'llâh': 'Allah\'a hamd olsun',
    'güm-râh': 'Yolunu kaybetmiş, sapkın',
    'bî-nihâyet': 'Sonsuz, nihayetsiz',
    'bî-karâr': 'Kararsız, huzursuz',
    'bî-gümân': 'Şüphesiz, kuşkusuz',
    'bî-nişân': 'İşaretsiz, belirsiz, sıfatsız',
    'assı-ziyân': 'Kâr-zarar, fayda ve ziyan',
    'evvel-âhir': 'Baştan sona, ilk ve son',
    'ezel-ebed': 'Başlangıçsız ve sonsuz, ezelden ebede',
    'lâ-mekân': 'Mekansız, yersiz (Allah sıfatı)',
    'dün-gün': 'Gece gündüz, sürekli',
    'yir-gök': 'Yer ve gök, tüm kainat',
    'sen-ben': 'Benlik, ikilik',
    'tahte\'s-serâ': 'Yerin altı, toprak altı',
    'sâz-kâr': 'Uygun, elverişli, yarar',
    'dünyâ-âhiret': 'Dünya ve ahiret, bu dünya ve öte',
    'âsil-zâdeler': 'Asil soydan gelenler, soylular',
    'âsil-zâde': 'Asil soydan gelen, soylu',
    'âb-ı': 'Su (izafet: ...suyu)',
    'zehr-i': 'Zehir (izafet: ...zehiri)',
    'deryâ-yı': 'Deniz (izafet: ...denizi)',
    'safâ-nazarı': 'Saf bakış, temiz nazar, mürşidin bakışı',
    'n\'idelüm': 'Ne edelim',
    'n\'ideyin': 'Ne edeyim',
}

def find_compound_meaning(word, sozluk):
    """Find meaning of a hyphenated compound word."""
    w = word.lower().strip("'\".,;:!?()-–")
    if w in COMPOUND_MEANINGS:
        return COMPOUND_MEANINGS[w]
    # Try without suffix (e.g. bî-çâresüz → bî-çâre)
    for s in ['si', 'sı', 'yi', 'yı', 'nün', 'nun', 'den', 'dan', 'ye', 'ya']:
        if w.endswith(s) and w[:-len(s)] in COMPOUND_MEANINGS:
            return COMPOUND_MEANINGS[w[:-len(s)]]
    return None

def find_meaning(word, sozluk):
    """Find meaning of a word in the glossary. Only exact or very close matches."""
    w = normalize(word)
    if not w or len(w) <= 2:
        return None
    
    # Skip common Turkish words that don't need explanation
    common = {'bir', 'ben', 'sen', 'biz', 'siz', 'var', 'yok', 'kim', 'ile', 'hem',
              'her', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz', 'on',
              'bin', 'yüz', 'gel', 'git', 'ver', 'gör', 'bak', 'dur', 'tur', 'kıl',
              'olan', 'ola', 'olur', 'oldu', 'ider', 'eder', 'dir', 'dür', 'ana', 'ata',
              'içün', 'için', 'gibi', 'dahi', 'dahı', 'bile', 'yine', 'gine',
              'ise', 'çün', 'çünki', 'eger', 'ger', 'niçe', 'nice', 'nite',
              'kanda', 'anda', 'bunda', 'sana', 'bana', 'anun', 'bunun', 'senün', 'benüm',
              'olsa', 'ola', 'gele', 'gide', 'kala', 'tura', 'diye', 'eyde', 'söyle',
              'degül', 'degil', 'gerek', 'yok', 'var', 'ola', 'olan', 'iken', 'imiş',
              'kişi', 'kişinün', 'cümle', 'hep', 'şol', 'oldı',
              'başum', 'başı', 'yüzin', 'yüzi', 'gözüm', 'gözi', 'dilüm', 'dili',
              'bilüm', 'bilür', 'bilmez', 'bildi', 'geldi', 'gitdi', 'virdi', 'aldı',
              # verb forms of eyle- (to do) — prevent false match with adverb 'eyle'
              'eyleye', 'eyleyem', 'eyleyen', 'eyleyüp', 'eylegil', 'eyledi',
              'eylemez', 'eylemek', 'eyledüm', 'eyledük', 'eyleriz', 'eylerüz',
              'eylese', 'eylesün', 'eylesin', 'eylemege', 'eylemedi',
              # other common verb forms that shouldn't get wrong tooltips
              'gönülde', 'gönüle', 'gönüller', 'gönüllerde',
              }
    if w in common:
        return None
    
    # Pattern-based skip: common verb roots + recognizable suffix = no tooltip
    common_roots = {'ol','gel','git','ver','vir','al','bul','kal','bil','gör',
        'dur','tur','kıl','et','it','eyle','de','di','ye','iç','yaz','oku',
        'çık','gir','geç','düş','at','tut','sat','kes','aç','yap','bak',
        'sor','sev','öl','doğ','ağla','gül','sus','dinle','bekle',
        'iste','san','say','dön','bırak','koy','koş','yürü','otur','kalk',
        'yat','kaç','söyle','ara','bat','yan','duy','sun','var',
        'çek','sür','yak','dol','tol','vur','kur','boz',
        'yara','yarat','kod','sakın',
        'ide','eyde','dile','anla','düşün',
        'gid','dön','geç','bin','koş',
        'sev','özen','utan','kork','sevin','acı',
        'götür','getir','göster','tanı','başla',
        'bekle','dayan','eriş','iriş','yet','ulaş',
        'tut','geçir','yürü','gez','uç',
        'sar','bağla','çöz','ört','giy','taşı','yıka','sil',
        'öldür','dirilt','yaşa','büyü',
        'gönder','yolla','düşür','kaldır',
        'güldür','ağlat','korkut',
        'hatırla','sabret',
        'iste','dile','yalvar',
        'anma','gör','bil','sor','söyle','diy',
    }
    # Only match roots of length >= 3 to avoid false positives with 'an','al','at' etc.
    verb_suffixes = {'mak','mek','maga','mege','maya','meye',
        'dı','di','du','dü','tı','ti','tu','tü',
        'düm','dum','dim','dım','tüm','tum',
        'dün','dun','din','dın',
        'mış','miş','muş','müş',
        'ür','ur','ir','ır','er','ar',
        'maz','mez','mez','maz',
        'ıp','ip','up','üp','üben','ıban',
        'sün','sun','sin','sın',
        'alum','elüm','alım','elim',
        'ayın','eyin','ayım','eyim',
        'am','em','um','üm',
        'eler','alar','iler','ılar',
        'en','an',
        'esi','ası','esin','asın',
        'ınca','ince','unca','ünce',
        'ıcak','icek','ucak','ücek',
        'dukça','dükçe','dıkça','dikçe',
        'iken','üken',
        'arak','erek',
        'e','a',  # optative: gele, vara, kıla
    }
    if len(w) > 4:
        for slen in range(min(len(w)-3, 6), 0, -1):
            root = w[:-slen]
            suffix = w[len(root):]
            if len(root) >= 3 and root in common_roots and suffix in verb_suffixes:
                return None
    
    # Check extra meanings first (try both with and without apostrophe)
    if w in EXTRA_MEANINGS:
        return EXTRA_MEANINGS[w]
    # Try with apostrophe preserved (for words like ma'şûka)
    w_with_apos = word.lower().strip("\".,;:!?()-–")
    if w_with_apos in EXTRA_MEANINGS:
        return EXTRA_MEANINGS[w_with_apos]
    
    # Direct match in glossary
    if w in sozluk:
        return shorten(sozluk[w])
    
    # Try without diacritics
    w_plain = w.replace('â', 'a').replace('î', 'i').replace('û', 'u')
    if w_plain != w and w_plain in sozluk:
        return shorten(sozluk[w_plain])
    if w_plain in EXTRA_MEANINGS:
        return EXTRA_MEANINGS[w_plain]
    
    # Try removing apostrophe
    w_noapos = w.replace("'", "")
    if w_noapos != w and w_noapos in sozluk:
        return shorten(sozluk[w_noapos])
    
    # Try verb root + mak/mek (only for words > 4 chars)
    if len(w) > 4:
        for suffix in ['mak', 'mek']:
            if w + suffix in sozluk:
                return shorten(sozluk[w + suffix])
    
    # Try removing common suffixes to find root
    suffixes = ['lerinden', 'larından', 'leründen', 'larundan',
                'ligünden', 'lığından', 'lügünden', 'luğundan',
                'ligüne', 'lığına', 'lügüne', 'luğuna',
                'ligün', 'lığın', 'lügün', 'luğun',
                'lige', 'lığa', 'lüge', 'luğa',  # dative of -lik
                'ligi', 'lığı', 'lügi', 'luğu',  # accusative of -lik
                'lerün', 'larun', 'lerine', 'larına',
                'lere', 'lara',
                'ıdur', 'idür', 'udur', 'üdür',
                'ıdı', 'idi', 'udı', 'üdi',
                'dür', 'dur', 'dir', 'dır',
                'ler', 'lar', 'leri', 'ları',
                'ünden', 'unden', 'inden', 'ından',
                'nün', 'nun', 'nın', 'nin',
                'dan', 'den', 'tan', 'ten',
                'sın', 'sin', 'sun', 'sün',
                'ına', 'ine', 'una', 'üne',
                'ını', 'ini', 'unu', 'ünü',
                'ıla', 'ile', 'ula', 'üle',
                'suz', 'süz', 'sız', 'siz',
                'lık', 'lik', 'luk', 'lük',
                'lıg', 'lig', 'lug', 'lüg',
                'ın', 'in', 'un', 'ün',
                'ım', 'im', 'um', 'üm',
                'ya', 'ye', 'na', 'ne',
                'da', 'de', 'ta', 'te',
                'ı', 'i', 'u', 'ü']
    for s in sorted(suffixes, key=len, reverse=True):
        if w.endswith(s) and len(w) > len(s) + 2:
            root = w[:-len(s)]
            if root in sozluk:
                return shorten(sozluk[root])
            if root in EXTRA_MEANINGS:
                return EXTRA_MEANINGS[root]
            # Also try root without diacritics
            root_plain = root.replace('â', 'a').replace('î', 'i').replace('û', 'u')
            if root_plain != root:
                if root_plain in sozluk:
                    return shorten(sozluk[root_plain])
                if root_plain in EXTRA_MEANINGS:
                    return EXTRA_MEANINGS[root_plain]
    
    return None

def annotate_poem(poem, sozluk):
    """Annotate a single poem with word meanings."""
    annotated_beyitler = []
    
    for beyit in poem['beyitler']:
        text = beyit['metin']
        # Split into words (include hyphens to catch compounds)
        words = re.findall(r"[\w'âîûçşğöüÂÎÛÇŞĞÖÜ]+(?:-[\w'âîûçşğöüÂÎÛÇŞĞÖÜ]+)*", text)
        
        word_meanings = {}
        for word in words:
            if len(word) <= 2:  # Skip very short words
                continue
            # For hyphenated compounds, use the full form as key
            if '-' in word:
                compound_key = word.lower()
                meaning = find_compound_meaning(word, sozluk)
                if meaning:
                    word_meanings[compound_key] = meaning
            else:
                meaning = find_meaning(word, sozluk)
                if meaning:
                    word_meanings[word.lower()] = meaning
        
        annotated_beyitler.append({
            'numara': beyit['numara'],
            'metin': text,
            'anlamlar': word_meanings
        })
    
    return {
        'numara': poem['numara'],
        'bölüm': poem['bölüm'],
        'vezin': poem.get('vezin', ''),
        'beyitler': annotated_beyitler
    }

def main():
    divan, sozluk = load_data()
    
    annotated_poems = []
    total_annotations = 0
    
    for poem in divan['şiirler']:
        annotated = annotate_poem(poem, sozluk)
        annotated_poems.append(annotated)
        for b in annotated['beyitler']:
            total_annotations += len(b['anlamlar'])
    
    output = {
        'başlık': divan['başlık'],
        'hazırlayan': divan['hazırlayan'],
        'toplam_şiir': len(annotated_poems),
        'şiirler': annotated_poems
    }
    
    with open('data/divan_annotated.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {len(annotated_poems)} şiir açıklandı, toplam {total_annotations} kelime anlamı eklendi")
    print(f"✓ Çıktı: data/divan_annotated.json")

if __name__ == '__main__':
    main()
