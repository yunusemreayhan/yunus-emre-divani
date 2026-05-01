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
    return w

def shorten(meaning):
    """Get short version of a meaning."""
    # Take first definition segment
    short = meaning.split('.')[0] if '.' in meaning else meaning
    # Also try splitting on comma for very long ones
    if len(short) > 60:
        short = short.split(',')[0]
    if len(short) > 80:
        short = short[:77] + '...'
    return short.strip()

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
    'sırât': 'Cehennem üzerindeki köprü',
    'hûrî': 'Cennet güzeli',
}

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
              'içün', 'için', 'gibi', 'bigi', 'dahi', 'dahı', 'bile', 'yine', 'gine',
              'ise', 'çün', 'çünki', 'eger', 'ger', 'niçe', 'nice', 'nite', 'kanı',
              'kanda', 'anda', 'bunda', 'sana', 'bana', 'anun', 'bunun', 'senün', 'benüm',
              'olsa', 'ola', 'gele', 'gide', 'kala', 'tura', 'diye', 'eyde', 'söyle',
              'degül', 'degil', 'gerek', 'yok', 'var', 'ola', 'olan', 'iken', 'imiş',
              'kişi', 'kişinün', 'cümle', 'hep', 'şol', 'oldı',
              'başum', 'başı', 'yüzin', 'yüzi', 'gözüm', 'gözi', 'dilüm', 'dili',
              'bilüm', 'bilür', 'bilmez', 'bildi', 'geldi', 'gitdi', 'virdi', 'aldı'}
    if w in common:
        return None
    
    # Check extra meanings first
    if w in EXTRA_MEANINGS:
        return EXTRA_MEANINGS[w]
    
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
    suffixes = ['dür', 'dur', 'ler', 'lar', 'leri', 'ları', 'ünden', 'unden',
                'ından', 'inden', 'dan', 'den', 'ıdur', 'idür', 'ıdı', 'idi',
                'sın', 'sin', 'ına', 'ine', 'ını', 'ini', 'ıla', 'ile',
                'suz', 'süz', 'lık', 'lik', 'lıg', 'lig']
    for s in sorted(suffixes, key=len, reverse=True):
        if w.endswith(s) and len(w) > len(s) + 2:
            root = w[:-len(s)]
            if root in sozluk:
                return shorten(sozluk[root])
            if root in EXTRA_MEANINGS:
                return EXTRA_MEANINGS[root]
    
    return None

def annotate_poem(poem, sozluk):
    """Annotate a single poem with word meanings."""
    annotated_beyitler = []
    
    for beyit in poem['beyitler']:
        text = beyit['metin']
        # Split into words
        words = re.findall(r"[\w'âîûçşğöüÂÎÛÇŞĞÖÜ]+", text)
        
        word_meanings = {}
        for word in words:
            if len(word) <= 2:  # Skip very short words
                continue
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
