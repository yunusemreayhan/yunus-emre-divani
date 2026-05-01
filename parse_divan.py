#!/usr/bin/env python3
"""Parse the PDF-extracted Yunus Emre Divan text into structured JSON."""
import json, re, sys, os

SECTIONS = ["ELİF", "BE", "PE", "TE", "ÇE", "RA", "ZA", "SİN", "ŞIN", "GAYIN", "KÂF", "KEF", "LAM", "MİM", "NUN", "VÂV", "HE", "YA"]
METER_KEYWORDS = ["Müstef'ilün", "Mefâ'îlün", "Fâ'ilâtün", "Fe'ûlün", "Mef'ûlü", "Müfte'îlün"]
SOURCE_PREFIXES = ['F. ', 'F.', 'K. ', 'K.', 'T. ', 'RY.', 'RY ', 'NO.', 'YE.', 'Rt.', 'HB.', 'B. ', 'Ç.', 'Ç ', 'M. ', 'A. ', 'DTCF', 'Georg', 'Mecmûa', 'Dîvân,', 'Şiir ', 'Cönk', 'Câmiü', 'Mısır']

def is_meter(line):
    return any(m in line for m in METER_KEYWORDS)

def is_source(line):
    # Source lines typically start with "F. 55b" or similar
    if any(line.startswith(p) for p in SOURCE_PREFIXES):
        return True
    # Also match patterns like "F. 55b, T. 1b"
    if re.match(r'^[A-Z]+\.\s*\d', line):
        return True
    return False

def parse(text):
    # Find start of poems
    idx = text.find("\nELİF\n")
    if idx == -1:
        idx = text.find("ELİF\n")
    text = text[idx:] if idx != -1 else text
    
    # Find end
    for marker in ["SÖZLÜK", "ŞİİR İNDEKSİ"]:
        eidx = text.find("\n" + marker)
        if eidx != -1:
            text = text[:eidx]
    
    # Clean and tokenize
    raw_lines = text.split('\n')
    tokens = []  # (type, content) where type is: section, pageheader, number, meter, source, text, empty
    
    for line in raw_lines:
        l = line.strip().replace('\x0c', '').strip()
        if not l:
            tokens.append(('empty', ''))
        elif l == "Dr. Mustafa Tatcı" or l == "Yûnus Emre Dîvânı":
            tokens.append(('pageheader', l))
        elif l in SECTIONS:
            tokens.append(('section', l))
        elif re.match(r'^\d+$', l):
            tokens.append(('number', int(l)))
        elif is_meter(l):
            tokens.append(('meter', l))
        elif is_source(l):
            tokens.append(('source', l))
        else:
            tokens.append(('text', l))
    
    # Now parse tokens with state machine
    poems = []
    current_section = ""
    current_poem = None
    current_verse_num = None
    current_verse_text = ""
    
    # State: 'between_poems' or 'in_poem'
    state = 'between_poems'
    expected_next_poem = 1
    
    i = 0
    while i < len(tokens):
        ttype, tval = tokens[i]
        
        if ttype == 'empty' or ttype == 'pageheader':
            i += 1
            continue
        
        if ttype == 'section':
            current_section = tval
            state = 'between_poems'
            i += 1
            continue
        
        if ttype == 'source':
            # End of current poem's verses
            if current_poem:
                if current_verse_num and current_verse_text:
                    current_poem['beyitler'].append({'numara': current_verse_num, 'metin': current_verse_text.strip()})
                    current_verse_num = None
                    current_verse_text = ""
            state = 'between_poems'
            # Skip source continuation lines
            i += 1
            while i < len(tokens) and tokens[i][0] in ('text', 'source', 'empty', 'pageheader'):
                if tokens[i][0] == 'text' and not is_source(tokens[i][1]):
                    # Check if this text is continuation of source (contains manuscript refs)
                    if re.match(r'^[A-Z]', tokens[i][1]) and ('.' in tokens[i][1] or ',' in tokens[i][1]):
                        i += 1
                        continue
                    break
                i += 1
            continue
        
        if ttype == 'number':
            num = tval
            
            if state == 'between_poems':
                # Numbers between poems: could be page number or poem number
                # Poem number if it's close to expected and followed by meter/verse
                if 1 <= num <= 420:
                    # Look ahead to see if this starts a poem
                    is_poem = False
                    for j in range(i+1, min(len(tokens), i+6)):
                        if tokens[j][0] == 'empty' or tokens[j][0] == 'pageheader':
                            continue
                        if tokens[j][0] == 'meter':
                            is_poem = True
                            break
                        if tokens[j][0] == 'number' and tokens[j][1] == 1:
                            is_poem = True
                            break
                        if tokens[j][0] == 'text':
                            # Text directly after number = poem start (no meter, verse 1 implicit)
                            is_poem = True
                            break
                        break
                    
                    if is_poem:
                        # Save previous poem
                        if current_poem and current_poem['beyitler']:
                            poems.append(current_poem)
                        
                        current_poem = {'numara': num, 'bölüm': current_section, 'vezin': '', 'beyitler': []}
                        current_verse_num = None
                        current_verse_text = ""
                        state = 'in_poem'
                        expected_next_poem = num + 1
                        i += 1
                        continue
                
                # Skip (page number)
                i += 1
                continue
            
            elif state == 'in_poem':
                # Inside a poem: this number is a verse number
                if 1 <= num <= 50:
                    if current_verse_num and current_verse_text:
                        current_poem['beyitler'].append({'numara': current_verse_num, 'metin': current_verse_text.strip()})
                    current_verse_num = num
                    current_verse_text = ""
                    i += 1
                    continue
                else:
                    # Unexpected number inside poem - might be page number, skip
                    i += 1
                    continue
        
        if ttype == 'meter':
            if current_poem and not current_poem['beyitler']:
                current_poem['vezin'] = tval
            i += 1
            continue
        
        if ttype == 'text':
            if state == 'in_poem' and current_verse_num is not None:
                if current_verse_text:
                    current_verse_text += " " + tval
                else:
                    current_verse_text = tval
            elif state == 'in_poem' and current_verse_num is None:
                # Text right after poem number (no explicit verse 1)
                current_verse_num = 1
                current_verse_text = tval
            i += 1
            continue
        
        i += 1
    
    # Save last poem
    if current_poem:
        if current_verse_num and current_verse_text:
            current_poem['beyitler'].append({'numara': current_verse_num, 'metin': current_verse_text.strip()})
        if current_poem['beyitler']:
            poems.append(current_poem)
    
    return poems


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'divan_raw.txt'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    poems = parse(text)
    
    os.makedirs('data', exist_ok=True)
    output = {
        'başlık': 'Yûnus Emre Dîvânı',
        'hazırlayan': 'Yrd. Doç. Dr. Mustafa Tatcı',
        'toplam_şiir': len(poems),
        'şiirler': poems
    }
    
    with open('data/divan.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {len(poems)} şiir başarıyla ayrıştırıldı → data/divan.json")
    # Sanity check
    for p in poems[:10]:
        print(f"  #{p['numara']:3d} ({p['bölüm']:5s}): {len(p['beyitler']):2d} beyit | {p['beyitler'][0]['metin'][:55]}...")
    if len(poems) > 10:
        print(f"  ... ve {len(poems)-10} şiir daha")


if __name__ == '__main__':
    main()
