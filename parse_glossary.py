#!/usr/bin/env python3
"""Extract the SÖZLÜK (glossary) from the Divan PDF text into a JSON dictionary."""
import json, re, os

def parse_glossary(text):
    # Find glossary section
    idx = text.find("SÖZLÜK")
    if idx == -1:
        return {}
    text = text[idx:]
    
    # Clean form feeds and page headers
    text = re.sub(r'\x0c\d+\s*\n\s*Yûnus Emre Dîvânı\s*\n', '\n', text)
    text = re.sub(r'\x0c', '', text)
    text = re.sub(r'\nDr\. Mustafa Tatcı\s*\n', '\n', text)
    text = re.sub(r'\nYûnus Emre Dîvânı\s*\n', '\n', text)
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
    
    lines = text.split('\n')
    glossary = {}
    current_word = None
    current_def = ""
    
    # Pattern: Word(origin): Definition
    # or Word/Word2(origin): Definition
    entry_pattern = re.compile(r'^([^:]+?)\s*[\(\[]([aftr\.\s,]+)[\)\]]\s*:\s*(.+)$')
    entry_pattern2 = re.compile(r'^([A-ZÂÎÛÇŞĞÖÜa-zâîûçşğöü\'\-\s/ü]+)\s*[\(\[]([^)\]]+)[\)\]]\s*:\s*(.+)$')
    entry_pattern3 = re.compile(r'^([A-ZÂÎÛÇŞĞÖÜa-zâîûçşğöü\'\-\s/]+):\s*(.+)$')
    
    for line in lines[1:]:  # Skip "SÖZLÜK" header
        line = line.strip()
        if not line:
            continue
        if line.startswith('-') and line.endswith('-'):
            # Section header like -A-, -B-
            if current_word and current_def:
                glossary[current_word.lower()] = current_def.strip()
            current_word = None
            current_def = ""
            continue
        
        # Try to match entry patterns
        m = entry_pattern2.match(line)
        if not m:
            m = entry_pattern3.match(line)
        
        if m:
            # Save previous entry
            if current_word and current_def:
                glossary[current_word.lower()] = current_def.strip()
            
            if m.lastindex == 3:
                current_word = m.group(1).strip()
                current_def = m.group(3).strip()
            else:
                current_word = m.group(1).strip()
                current_def = m.group(2).strip()
        elif current_word:
            # Continuation of previous definition
            current_def += " " + line
    
    # Save last entry
    if current_word and current_def:
        glossary[current_word.lower()] = current_def.strip()
    
    return glossary


def main():
    with open('divan_raw.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    glossary = parse_glossary(text)
    
    os.makedirs('data', exist_ok=True)
    with open('data/sozluk.json', 'w', encoding='utf-8') as f:
        json.dump(glossary, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {len(glossary)} kelime sözlüğe aktarıldı → data/sozluk.json")
    # Show samples
    for i, (k, v) in enumerate(list(glossary.items())[:10]):
        print(f"  {k}: {v[:60]}...")


if __name__ == '__main__':
    main()
